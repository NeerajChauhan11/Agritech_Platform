"""Endpoints for querying farms, fields, and topology."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.common import ApiResponse
from app.schemas.farm import Farm, FieldSchema
from app.services.farm_service import farm_service

router = APIRouter(prefix="/farms", tags=["Farms & Fields"])


@router.get("", response_model=ApiResponse[list[Farm]])
async def list_farms() -> ApiResponse[list[Farm]]:
    """List all farms for the current context."""
    farms = await farm_service.get_all_farms()
    return ApiResponse(success=True, data=farms)


@router.get("/{farm_id}", response_model=ApiResponse[Farm])
async def get_farm_details(farm_id: str) -> ApiResponse[Farm]:
    """Retrieve details for a single farm."""
    farm = await farm_service.get_farm(farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FARM_NOT_FOUND", "message": f"Farm '{farm_id}' not found."},
        )
    return ApiResponse(success=True, data=farm)


@router.get("/{farm_id}/fields", response_model=ApiResponse[list[FieldSchema]])
async def list_farm_fields(farm_id: str) -> ApiResponse[list[FieldSchema]]:
    """List all fields inside a specific farm."""
    fields = await farm_service.get_fields_for_farm(farm_id)
    return ApiResponse(success=True, data=fields)


@router.get("/{farm_id}/fields/{field_id}", response_model=ApiResponse[FieldSchema])
async def get_field_details(farm_id: str, field_id: str) -> ApiResponse[FieldSchema]:
    """Retrieve a single field with device statuses and latest sensor reading."""
    field = await farm_service.get_field(farm_id, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FIELD_NOT_FOUND", "message": f"Field '{field_id}' not found in farm '{farm_id}'."},
        )
    return ApiResponse(success=True, data=field)
