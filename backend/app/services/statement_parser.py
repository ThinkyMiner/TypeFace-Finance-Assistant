import re
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pdfplumber
import camelot
from pathlib import Path

class StatementParser:
    def __init__(self):
        self.common_headers = {
            'date': ['date', 'transaction date', 'posting date', 'txn date'],
            'description': ['description', 'particulars', 'narration', 'details', 'transaction details'],
            'amount': ['amount', 'txn amount', 'transaction amount'],
            'debit': ['debit', 'withdrawal', 'dr', 'debit amount'],
            'credit': ['credit', 'deposit', 'cr', 'credit amount'],
            'balance': ['balance', 'running balance', 'available balance']
        }

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

            # Extract description
            description = ""
            if 'description' in header_mapping:
                description = str(row[header_mapping['description']]).strip()

            # Extract amount (try debit/credit columns first, then amount)
            amount = None
            kind = None

            if 'debit' in header_mapping and 'credit' in header_mapping:
                debit_val = self._parse_amount(str(row[header_mapping['debit']]))
                credit_val = self._parse_amount(str(row[header_mapping['credit']]))

                if debit_val and debit_val > 0:
                    amount = debit_val
                    kind = "expense"
                elif credit_val and credit_val > 0:
                    amount = credit_val
                    kind = "income"
            elif 'amount' in header_mapping:
                amount = self._parse_amount(str(row[header_mapping['amount']]))
                # Try to determine if it's income or expense from description or amount sign
                if description and any(word in description.lower() for word in ['salary', 'deposit', 'credit', 'interest']):
                    kind = "income"
                else:
                    kind = "expense"

            if not amount or amount <= 0:
                return None

            return {
                "occurred_on": date_val.isoformat(),
                "amount": amount,
                "kind": kind or "expense",
                "merchant": description[:100] if description else "Bank Transaction",
                "note": description[:500] if description else None,
                "category_id": None,  # Will be assigned by user or auto-categorization
                "payment_method": "bank_transfer"
            }

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