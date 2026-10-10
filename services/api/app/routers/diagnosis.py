"""Automatic crop disease diagnosis router."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.crops import require_supported_crop
from app.schemas.common import ApiResponse
from app.schemas.diagnosis import DiagnosisResult, ModelAvailability
from app.services.diagnosis_service import diagnosis_service

router = APIRouter(tags=["Diagnosis"])


@router.post("/diagnose", response_model=ApiResponse[DiagnosisResult])
async def diagnose_crop(
    file: Annotated[UploadFile, File(description="Leaf image file")],
    crop: Annotated[
        str | None,
        Form(deprecated=True, description="Deprecated and ignored: the crop is identified automatically."),
    ] = None,
) -> ApiResponse[DiagnosisResult]:
    """Identify the crop in an uploaded leaf photo and diagnose its disease."""
    if crop is not None:
        require_supported_crop(crop)  # validated (CROP_NOT_SUPPORTED) but never used for routing
    content = await file.read()
    try:
        result = await diagnosis_service.diagnose_leaf_image(content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_IMAGE_PAYLOAD", "message": str(exc)},
        ) from exc
    return ApiResponse(success=True, data=result)


@router.get("/diagnose/models", response_model=ApiResponse[list[ModelAvailability]])
async def list_diagnosis_models() -> ApiResponse[list[ModelAvailability]]:
    """Report which per-crop specific models and the general-category tier have weights installed."""
    return ApiResponse(success=True, data=diagnosis_service.model_report())
