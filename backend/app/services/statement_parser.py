import re
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pdfplumber
import camelot
from pathlib import Path
import google.generativeai as genai
from app.core.config import settings
import json

class StatementParser:
    def __init__(self):
        self.common_headers = {
            'date': ['date', 'transaction date', 'posting date', 'txn date'],
            'type': ['type', 'transaction type', 'txn type'],  # For our exported PDFs
            'merchant': ['merchant', 'description', 'particulars', 'narration', 'details', 'transaction details'],
            'amount': ['amount', 'txn amount', 'transaction amount', 'amount (inr)'],
            'payment_method': ['payment method', 'payment mode', 'mode'],
            'debit': ['debit', 'withdrawal', 'dr', 'debit amount'],
            'credit': ['credit', 'deposit', 'cr', 'credit amount'],
            'balance': ['balance', 'running balance', 'available balance']
        }
        self.use_gemini = bool(settings.GEMINI_API_KEY)
        if self.use_gemini:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    async def parse_statement(self, file_path: str, user_id: int) -> Dict[str, Any]:
        file_path = Path(file_path)

        try:
            # Try different parsing methods
            transactions = []

            # Method 1: Try camelot (for tabular PDFs)
            try:
                transactions = await self._parse_with_camelot(file_path)
                if transactions:
                    return {
                        "transactions": transactions,
                        "method": "camelot",
                        "success": True,
                        "message": f"Successfully parsed {len(transactions)} transactions"
                    }
            except Exception as e:
                print(f"Camelot parsing failed: {e}")

            # Method 2: Try pdfplumber text extraction
            try:
                transactions = await self._parse_with_pdfplumber(file_path)
                if transactions:
                    return {
                        "transactions": transactions,
                        "method": "pdfplumber",
                        "success": True,
                        "message": f"Successfully parsed {len(transactions)} transactions"
                    }
            except Exception as e:
                print(f"PDFplumber parsing failed: {e}")

            return {
                "transactions": [],
                "method": "none",
                "success": False,
                "message": "Unable to extract transaction data from the statement"
            }

        except Exception as e:
            return {
                "transactions": [],
                "method": "error",
                "success": False,
                "message": f"Error processing statement: {str(e)}"
            }

    async def _enhance_with_gemini(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use Gemini AI to improve income/expense classification"""
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')

            # Process in batches of 20
            batch_size = 20
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i + batch_size]

                # Create prompt
                txn_list = "\n".join([
                    f"{idx}. Date: {t['occurred_on']}, Description: {t.get('merchant', 'N/A')}, Amount: ₹{t['amount']}, Current Type: {t['kind']}"
                    for idx, t in enumerate(batch)
                ])

                prompt = f"""Analyze these bank transactions and classify each as "income" or "expense":

{txn_list}

Rules:
- INCOME: Salary, deposits, refunds, interest earned, money received, credits, reversals
- EXPENSE: Purchases, withdrawals, payments made, debits, transfers out, bills

Return ONLY a JSON array with the index and correct type for each transaction:
[{{"index": 0, "kind": "income"}}, {{"index": 1, "kind": "expense"}}, ...]"""

                response = model.generate_content(prompt)
                result_text = response.text.strip()

                # Clean markdown
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                classifications = json.loads(result_text.strip())

                # Apply classifications
                for item in classifications:
                    idx = item['index']
                    if idx < len(batch):
                        batch[idx]['kind'] = item['kind']

            print(f"[AI] Enhanced {len(transactions)} transactions with Gemini classification")
            return transactions

        except Exception as e:
            print(f"Gemini enhancement failed: {e}, using original classifications")
            return transactions

    async def _parse_with_camelot(self, file_path: Path) -> List[Dict[str, Any]]:
        # Try both stream and lattice methods
        tables = []

        # Try lattice method first (works better for structured tables)
        try:
            tables = camelot.read_pdf(str(file_path), flavor='lattice', pages='all')
        except:
            pass

        # If no tables found, try stream method
        if not tables or len(tables) == 0:
            try:
                tables = camelot.read_pdf(str(file_path), flavor='stream', pages='all')
            except:
                return []

        transactions = []
        for table in tables:
            df = table.df

            # Skip if table is too small
            if len(df) < 2:
                continue

            # Try to identify column headers
            header_mapping = self._map_headers(df.iloc[0].tolist())

            if not header_mapping.get('date'):
                # Try second row as headers
                header_mapping = self._map_headers(df.iloc[1].tolist())
                start_row = 2
            else:
                start_row = 1

            # Extract transactions
            for _, row in df.iloc[start_row:].iterrows():
                transaction = self._extract_transaction_from_row(row.tolist(), header_mapping)
                if transaction:
                    transactions.append(transaction)

        return transactions

    async def _parse_with_pdfplumber(self, file_path: Path) -> List[Dict[str, Any]]:
        transactions = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Try to extract tables from the page
                tables = page.extract_tables()

                for table in tables:
                    if len(table) < 2:
                        continue

                    # Find header row
                    header_mapping = None
                    start_row = 0

                    for i, row in enumerate(table[:3]):  # Check first 3 rows for headers
                        mapping = self._map_headers(row)
                        if mapping.get('date') or mapping.get('amount'):
                            header_mapping = mapping
                            start_row = i + 1
                            break

                    if not header_mapping:
                        continue

                    # Extract transactions
                    for row in table[start_row:]:
                        transaction = self._extract_transaction_from_row(row, header_mapping)
                        if transaction:
                            transactions.append(transaction)

        return transactions

    def _map_headers(self, headers: List[str]) -> Dict[str, int]:
        mapping = {}

        headers_lower = [str(h).lower().strip() if h else '' for h in headers]

        for field, possible_names in self.common_headers.items():
            for i, header in enumerate(headers_lower):
                for name in possible_names:
                    if name in header and len(header) > 0:
                        mapping[field] = i
                        break
                if field in mapping:
                    break

        return mapping

    def _extract_transaction_from_row(self, row: List[str], header_mapping: Dict[str, int]) -> Optional[Dict[str, Any]]:
        if not row or not header_mapping:
            return None

        try:
            # Extract date
            date_val = None
            if 'date' in header_mapping:
                date_str = str(row[header_mapping['date']]).strip()
                date_val = self._parse_date(date_str)

            if not date_val:
                return None  # Skip rows without valid dates

            # Extract merchant/description
            merchant = ""
            if 'merchant' in header_mapping:
                merchant = str(row[header_mapping['merchant']]).strip()

            # Extract amount and kind
            amount = None
            kind = None

            # Method 1: Check for direct 'type' column (from our exported PDFs)
            if 'type' in header_mapping and header_mapping['type'] < len(row):
                type_str = str(row[header_mapping['type']]).strip().lower()
                print(f"[PARSER] Found Type column: '{type_str}'")

                if type_str in ['income', 'credit', 'deposit']:
                    kind = "income"
                elif type_str in ['expense', 'debit', 'withdrawal']:
                    kind = "expense"

                # Get amount from amount column
                if 'amount' in header_mapping:
                    amount_str = str(row[header_mapping['amount']]).strip()
                    # Remove currency symbol and "₹" if present
                    amount_str = amount_str.replace('₹', '').strip()
                    amount = self._parse_amount(amount_str)
                    print(f"[PARSER] Direct type parsing: {kind.upper()} ₹{amount}")

            # Method 2: Try debit/credit columns for bank statements
            elif 'debit' in header_mapping and 'credit' in header_mapping:
                debit_str = str(row[header_mapping['debit']]) if header_mapping['debit'] < len(row) else ''
                credit_str = str(row[header_mapping['credit']]) if header_mapping['credit'] < len(row) else ''

                debit_val = self._parse_amount(debit_str)
                credit_val = self._parse_amount(credit_str)

                print(f"[PARSER] Debit: '{debit_str}' -> {debit_val}, Credit: '{credit_str}' -> {credit_val}")

                # Credit = Money IN = Income
                # Debit = Money OUT = Expense
                if credit_val and credit_val > 0:
                    amount = credit_val
                    kind = "income"
                    print(f"[PARSER] ✅ INCOME: ₹{amount} from credit column")
                elif debit_val and debit_val > 0:
                    amount = debit_val
                    kind = "expense"
                    print(f"[PARSER] ❌ EXPENSE: ₹{amount} from debit column")

            # Method 3: Single amount column with keyword detection
            elif 'amount' in header_mapping:
                amount = self._parse_amount(str(row[header_mapping['amount']]))
                # Try to determine if it's income or expense from description
                income_keywords = [
                    'salary', 'deposit', 'credit', 'interest', 'refund',
                    'reversal', 'cashback', 'payment received', 'transfer in',
                    'neft cr', 'imps cr', 'upi cr', 'credited', 'cr-'
                ]
                expense_keywords = [
                    'debit', 'withdrawal', 'payment', 'purchase', 'transfer out',
                    'neft dr', 'imps dr', 'upi dr', 'debited', 'dr-', 'pos'
                ]

                merchant_lower = merchant.lower() if merchant else ''

                # Check for income keywords
                if any(word in merchant_lower for word in income_keywords):
                    kind = "income"
                # Check for expense keywords
                elif any(word in merchant_lower for word in expense_keywords):
                    kind = "expense"
                # Default to expense if can't determine
                else:
                    kind = "expense"

            if not amount or amount <= 0:
                return None

            # Extract payment method if available
            payment_method = "bank_transfer"
            if 'payment_method' in header_mapping and header_mapping['payment_method'] < len(row):
                pm_str = str(row[header_mapping['payment_method']]).strip()
                if pm_str and pm_str.lower() not in ['', 'nan', 'none', '-']:
                    payment_method = pm_str.lower().replace(' ', '_')

            result = {
                "occurred_on": date_val.isoformat(),
                "amount": amount,
                "kind": kind or "expense",
                "merchant": merchant[:100] if merchant else "Bank Transaction",
                "note": merchant[:500] if merchant else None,
                "category_id": None,  # Will be assigned by user or auto-categorization
                "payment_method": payment_method
            }

            print(f"[PARSER] Final transaction: {result['occurred_on']} | {result['kind'].upper()} | ₹{result['amount']} | {result['merchant'][:30]}")
            return result

        except Exception as e:
            print(f"Error extracting transaction from row: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        if not date_str or date_str.lower() in ['', 'nan', 'none']:
            return None

        # Common date formats in bank statements
        formats = [
            '%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%m/%d/%Y', '%m/%d/%y',
            '%d %b %Y', '%d %B %Y', '%b %d %Y', '%B %d %Y',
            '%d-%b-%Y', '%d-%B-%Y'
        ]

        # Clean the date string
        date_str = re.sub(r'[^\w\s/-]', '', date_str).strip()

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        if not amount_str or amount_str.lower() in ['', 'nan', 'none', '-']:
            return None

        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.-]', '', str(amount_str).replace(',', ''))

        try:
            amount = float(cleaned)
            return abs(amount)  # Always return positive amount
        except (ValueError, TypeError):
            return None