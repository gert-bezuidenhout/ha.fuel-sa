"""Offline tests against Fuel SA's documented contract."""

import asyncio
from copy import deepcopy
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import MagicMock

import aiohttp

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load the API without importing the HA-dependent integration entry point.
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "_fuelsa_test"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT / "custom_components" / "fuelsa")]
sys.modules[PACKAGE] = package
spec = importlib.util.spec_from_file_location(
    f"{PACKAGE}.api", ROOT / "custom_components" / "fuelsa" / "api.py"
)
api = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = api
spec.loader.exec_module(api)


def fixture():
    return json.loads((ROOT / "tests/fixtures/current.json").read_text(encoding="utf-8-sig"))


class ParseTests(unittest.TestCase):
    def test_documented_response(self):
        prices = api.parse_prices(fixture())
        self.assertEqual(len(prices), 10)
        self.assertEqual(prices["reef_petrol_unleaded_95"].price, Decimal("13.40"))
        self.assertEqual(prices["coast_diesel_500_ppm"].price, Decimal("10.70"))
        self.assertIsNotNone(prices["reef_petrol_unleaded_95"].effective_at.tzinfo)

    def test_identity_survives_new_month(self):
        payload = fixture()
        old = set(api.parse_prices(payload))
        for row in payload["petrol"] + payload["diesel"]:
            row["date"] = "2020-07-01T00:00:00+02:00"
            row["_id"] = "different"
        self.assertEqual(set(api.parse_prices(payload)), old)

    def test_newest_duplicate_wins_independent_of_order(self):
        payload = fixture()
        newer = deepcopy(payload["petrol"][0])
        newer.update(date="2021-01-01T00:00:00Z", value=1501)
        for rows in ([newer] + payload["petrol"], payload["petrol"] + [newer]):
            payload["petrol"] = rows
            self.assertEqual(api.parse_prices(payload)["reef_petrol_lrp_95"].price, Decimal("15.01"))

    def test_invalid_responses(self):
        for payload in (None, [], {}, {"petrol": [], "diesel": []}, {"error": "denied"}):
            with self.subTest(payload=payload), self.assertRaises(api.FuelSAError):
                api.parse_prices(payload)
        for value in (None, True, "NaN", "Infinity", -100, "bad", 0):
            payload = fixture()
            payload["petrol"][0]["value"] = value
            with self.subTest(value=value), self.assertRaises(api.FuelSAError):
                api.parse_prices(payload)

    def test_missing_or_invalid_identity_and_date(self):
        for field, value in (("date", "bad"), ("date", "2020-01-01"), ("location", ""), ("octane", None)):
            payload = fixture()
            if value is None:
                del payload["petrol"][0][field]
            else:
                payload["petrol"][0][field] = value
            with self.subTest(field=field), self.assertRaises(api.FuelSAError):
                api.parse_prices(payload)


class Response:
    def __init__(self, status=200, payload=None, error=None):
        self.status, self.payload, self.error = status, payload, error

    async def __aenter__(self):
        if self.error:
            raise self.error
        return self

    async def __aexit__(self, *args):
        return False

    async def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_and_response(self):
        session = MagicMock()
        session.get.return_value = Response(payload=fixture())
        result = await api.FuelSAClient(session, "secret").async_get_prices()
        self.assertEqual(len(result), 10)
        args, kwargs = session.get.call_args
        self.assertEqual(args[0], "https://api.fuelsa.co.za/exapi/fuel/current")
        self.assertEqual(kwargs["headers"], {"key": "secret"})
        self.assertFalse(kwargs["allow_redirects"])

    async def test_auth_failures(self):
        for status in (401, 403):
            session = MagicMock()
            session.get.return_value = Response(status=status)
            with self.assertRaises(api.FuelSAAuthError):
                await api.FuelSAClient(session, "secret").async_get_prices()

    async def test_service_and_transport_failures(self):
        for response in (Response(status=429), Response(status=500), Response(status=302),
                         Response(payload=ValueError("invalid json")), Response(payload={}),
                         Response(error=asyncio.TimeoutError()),
                         Response(error=aiohttp.ClientConnectionError())):
            session = MagicMock()
            session.get.return_value = response
            with self.assertRaises(api.FuelSAError):
                await api.FuelSAClient(session, "secret").async_get_prices()


if __name__ == "__main__":
    unittest.main()
