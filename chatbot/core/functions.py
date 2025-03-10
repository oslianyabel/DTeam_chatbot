import logging

logger = logging.getLogger(__name__)


async def get_temperature_by_city(city: str) -> str:
    if city == "Habana":
        return "28 C"

    return "20 C"
