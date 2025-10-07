from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.core.security import get_current_user_id
from app.services.ocr import ReceiptExtractor
from typing import Dict, Any

router = APIRouter()

@router.post("/extract")
async def extract_receipt(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Check file size (limit to 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()

    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")

    # Check file type
    allowed_types = {'image/jpeg', 'image/png', 'image/jpg', 'application/pdf'}

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"File type {file.content_type} not supported. Allowed: {', '.join(allowed_types)}"
        )

    try:
        extractor = ReceiptExtractor()
        result = await extractor.extract_from_file(file_content, file.filename, current_user_id)

        return {
            "extracted": result,
            "message": "Receipt processed successfully. Review the extracted data before creating the transaction."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process receipt: {str(e)}")