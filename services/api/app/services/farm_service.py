"""Service for querying farm and field metadata."""

from app.core.config import settings
from app.demo import fixtures
from app.schemas.farm import Farm, FieldSchema


class FarmService:
    """Business operations for farms, fields, and sensor topology."""

    @staticmethod
    async def get_all_farms() -> list[Farm]:
        """Fetch all farms for the authenticated tenant."""
        if settings.DEMO_MODE:
            return [fixtures.DEMO_FARM]
        return [fixtures.DEMO_FARM]

    @staticmethod
    async def get_farm(farm_id: str) -> Farm | None:
        """Fetch single farm entity by unique identifier."""
        if settings.DEMO_MODE:
            if farm_id == fixtures.DEMO_FARM.id:
                return fixtures.DEMO_FARM
            return None
        return fixtures.DEMO_FARM if farm_id == fixtures.DEMO_FARM.id else None

    @staticmethod
    async def get_fields_for_farm(farm_id: str) -> list[FieldSchema]:
        """Fetch all fields associated with a farm."""
        farm = await FarmService.get_farm(farm_id)
        if not farm:
            return []
        return farm.fields

    @staticmethod
    async def get_field(farm_id: str, field_id: str) -> FieldSchema | None:
        """Fetch detailed single field record including devices and latest reading."""
        fields = await FarmService.get_fields_for_farm(farm_id)
        for field in fields:
            if field.id == field_id:
                return field
        return None


farm_service = FarmService()
