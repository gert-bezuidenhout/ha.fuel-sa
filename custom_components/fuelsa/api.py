"""Fuel SA transport and response parsing."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

import aiohttp

from .const import API_URL


class FuelSAError(Exception):
    """The service could not provide usable data."""


class FuelSAAuthError(FuelSAError):
    """The API key was rejected."""


@dataclass(frozen=True)
class FuelPrice:
    """One price; identity deliberately excludes database IDs and dates."""

    key: str
    name: str
    location: str
    fuel: str
    grade: str
    price: Decimal
    effective_at: datetime


def parse_prices(payload: object) -> dict[str, FuelPrice]:
    """Convert the documented cents/litre response to rand/litre."""
    if not isinstance(payload, dict):
        raise FuelSAError("Expected a price object")
    prices = {}
    try:
        for fuel in ("petrol", "diesel"):
            rows = payload[fuel]
            if not isinstance(rows, list):
                raise ValueError("Expected price arrays")
            for row in rows:
                location = row["location"].strip()
                grade = (f'{row["type"]} {row["octane"]}' if fuel == "petrol"
                         else f'{row["ppm"]} ppm')
                if not location or not grade.strip():
                    raise ValueError("Missing identity")
                value = row["value"]
                if isinstance(value, bool):
                    raise ValueError("Invalid price")
                price = Decimal(str(value)) / 100
                if not price.is_finite() or price <= 0:
                    raise ValueError("Invalid price")
                date = datetime.fromisoformat(row["date"].replace("Z", "+00:00"))
                if date.tzinfo is None:
                    raise ValueError("Missing time zone")
                key = re.sub(r"[^a-z0-9]+", "_", f"{location}_{fuel}_{grade}".lower()).strip("_")
                item = FuelPrice(key, f"{location} {fuel.title()} {grade}",
                                 location, fuel, grade, price, date)
                if key not in prices or date > prices[key].effective_at:
                    prices[key] = item
    except (KeyError, TypeError, ValueError, AttributeError, InvalidOperation) as err:
        raise FuelSAError("Invalid price response") from err
    if not prices:
        raise FuelSAError("No fuel prices returned")
    return prices


class FuelSAClient:
    """Use Home Assistant's shared HTTP session."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self.session = session
        self.api_key = api_key

    async def async_get_prices(self) -> dict[str, FuelPrice]:
        try:
            async with self.session.get(
                API_URL, headers={"key": self.api_key},
                timeout=aiohttp.ClientTimeout(total=30), allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise FuelSAAuthError("API key rejected")
                if response.status != 200:
                    raise FuelSAError(f"Fuel SA returned HTTP {response.status}")
                return parse_prices(await response.json())
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise FuelSAError("Unable to retrieve Fuel SA prices") from err
