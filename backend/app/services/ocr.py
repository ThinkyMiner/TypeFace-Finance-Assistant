import re
import os
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional, Any
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdfplumber
import magic
import google.generativeai as genai
from app.core.config import settings
import json
import base64

class ReceiptExtractor:
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True, parents=True)
        self.use_gemini = bool(settings.GEMINI_API_KEY)
        if self.use_gemini:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    async def extract_from_file(self, file_content: bytes, filename: str, user_id: int) -> Dict[str, Any]:
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix.lower()
        file_path = self.upload_dir / f"user_{user_id}" / f"{file_id}{file_ext}"
        file_path.parent.mkdir(exist_ok=True, parents=True)

        try:
            with open(file_path, "wb") as f:
                f.write(file_content)

            mime_type = magic.from_file(str(file_path), mime=True)

            # Use Gemini Vision if available for better accuracy
            if self.use_gemini and mime_type.startswith('image/'):
                extracted_data = await self._extract_with_gemini_vision(file_path, mime_type)
            else:
                # Fallback to traditional OCR
                if mime_type.startswith('image/'):
                    text = await self._extract_from_image(file_path)
                elif mime_type == 'application/pdf':
                    text = await self._extract_from_pdf(file_path)
                else:
                    raise ValueError(f"Unsupported file type: {mime_type}")

                extracted_data = self._parse_receipt_text(text)

            extracted_data["receipt_path"] = str(file_path)
            if "confidence" not in extracted_data:
                extracted_data["confidence"] = self._calculate_confidence(extracted_data)

            return extracted_data

        except Exception as e:
            # Clean up file on error
            if file_path.exists():
                os.unlink(file_path)
            raise e

    async def _extract_with_gemini_vision(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """
        Extract receipt data using Gemini 2.5 Flash vision model
        This provides much better accuracy than traditional OCR
        """
        try:
            # Read the image file
            with open(file_path, 'rb') as f:
                image_data = f.read()

            # Upload the image to Gemini
            model = genai.GenerativeModel('gemini-2.5-flash-latest')

            # Create the prompt for receipt extraction
            prompt = """You are a receipt OCR expert. Analyze this POS receipt image and extract the following information in JSON format:

{
  "merchant": "Name of the store/merchant",
  "date": "Date in YYYY-MM-DD format",
  "amount": "Total amount as a number (without currency symbol)",
  "items": ["list of items purchased"],
  "payment_method": "Payment method if visible (e.g., Cash, Card, UPI)",
  "note": "Any additional relevant information"
}

Instructions:
- Extract the TOTAL amount (not subtotal)
- If date is not clear, use today's date
- Be accurate with numbers
- If merchant name is not clear, extract the most prominent business name
- Return ONLY valid JSON, no other text

Receipt image:"""

            # Prepare the image for Gemini
            image_parts = [
                {
                    "mime_type": mime_type,
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]

            # Generate content
            response = model.generate_content([prompt, {"mime_type": mime_type, "data": image_data}])

            # Parse the response
            result_text = response.text.strip()

            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            extracted_data = json.loads(result_text.strip())

            # Format the data to match expected structure
            formatted_data = {
                "merchant": extracted_data.get("merchant"),
                "date": extracted_data.get("date"),
                "amount": float(extracted_data.get("amount")) if extracted_data.get("amount") else None,
                "payment_method": extracted_data.get("payment_method"),
                "note": extracted_data.get("note", ""),
                "items": extracted_data.get("items", []),
                "confidence": 0.95,  # Gemini is very accurate
                "extraction_method": "gemini_vision"
            }

            return formatted_data

        except json.JSONDecodeError as e:
            # Fallback to traditional OCR if JSON parsing fails
            print(f"Gemini JSON parsing failed: {e}, falling back to OCR")
            text = await self._extract_from_image(file_path)
            return self._parse_receipt_text(text)
        except Exception as e:
            print(f"Gemini vision extraction failed: {e}, falling back to OCR")
            text = await self._extract_from_image(file_path)
            return self._parse_receipt_text(text)

    async def _extract_from_image(self, file_path: Path) -> str:
        image = cv2.imread(str(file_path))

        # Preprocess image for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Noise removal
        denoised = cv2.medianBlur(gray, 3)

        # Thresholding to get better contrast
        _, threshold = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convert to PIL Image for tesseract
        pil_image = Image.fromarray(threshold)

        # Extract text using tesseract
        text = pytesseract.image_to_string(pil_image, config='--psm 6')

        return text

    async def _extract_from_pdf(self, file_path: Path) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # If no text found, try OCR on PDF pages
        if not text.strip():
            # Convert PDF pages to images and OCR
            import fitz  # PyMuPDF - we'd need to add this to requirements
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2, 2)  # 2x zoom
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")

                # Convert to OpenCV image
                nparr = np.frombuffer(img_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # OCR the image
                text += pytesseract.image_to_string(image, config='--psm 6') + "\n"
            doc.close()

        return text

    def _parse_receipt_text(self, text: str) -> Dict[str, Any]:
        result = {
            "date": None,
            "amount": None,
            "merchant": None,
            "note": text.strip()[:500],  # First 500 chars as note
            "matched_category": None
        }

        # Extract amount (look for currency patterns)
        amount_patterns = [
            r'(?:total|amount|subtotal|sum|₹|inr|rs\.?)\s*:?\s*(\d+(?:[,\.]\d+)?)',
            r'(\d+(?:[,\.]\d+)?)\s*(?:₹|inr|rs\.?)',
            r'\$\s*(\d+(?:\.\d{2})?)',
            r'(\d+\.\d{2})\s*$',  # Standalone decimal amount
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    result["amount"] = float(amount_str)
                    break
                except ValueError:
                    continue

        # Extract date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    result["date"] = parsed_date.isoformat()
                    break

        # Extract merchant (usually first significant line or after common keywords)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Try to find merchant name (first meaningful line that's not a date/amount)
            for line in lines[:5]:  # Check first 5 lines
                if len(line) > 3 and not re.match(r'^\d+[/-]\d+', line) and not re.search(r'\d+\.\d{2}', line):
                    # Clean up the line (remove extra spaces, common receipt words)
                    merchant = re.sub(r'\s+', ' ', line.upper())
                    merchant = re.sub(r'\b(RECEIPT|BILL|INVOICE|TAX|GST)\b', '', merchant).strip()
                    if merchant and len(merchant) > 2:
                        result["merchant"] = merchant[:100]  # Limit length
                        break

        return result

    def _parse_date(self, date_str: str) -> Optional[date]:
        date_formats = [
            '%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y',
            '%d %b %Y', '%d %B %Y'
        ]

        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                return parsed.date()
            except ValueError:
                continue

        return None

    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        confidence = 0.0

        # Award points for each successfully extracted field
        if extracted_data["amount"] is not None:
            confidence += 0.4  # Amount is most important
        if extracted_data["date"] is not None:
            confidence += 0.3
        if extracted_data["merchant"] is not None:
            confidence += 0.2
        if extracted_data["note"] and len(extracted_data["note"]) > 10:
            confidence += 0.1

        return min(confidence, 1.0)