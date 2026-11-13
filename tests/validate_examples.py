"""Offline validation of example YAML and Jinja; no notifications are sent."""

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from xml.etree import ElementTree

from jinja2 import Environment, StrictUndefined
from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[1]
automation = yaml.safe_load((ROOT / "examples/fuel_price_notification.yaml").read_text(encoding="utf-8"))
card = yaml.safe_load((ROOT / "examples/fuel_prices_card.yaml").read_text(encoding="utf-8"))


def is_number(value):
    try:
        return float("-inf") < float(value) < float("inf")
    except (TypeError, ValueError):
        return False


env = Environment(undefined=StrictUndefined)
env.globals.update(is_number=is_number, as_timestamp=lambda value: datetime.fromisoformat(value).timestamp())
env.filters["timestamp_custom"] = lambda value, fmt, local: datetime.fromtimestamp(value, timezone.utc).strftime(fmt)


def state(value):
    return SimpleNamespace(state=value, attributes={"friendly_name": "Fuel SA Reef Diesel 50 ppm", "fuel": "diesel", "effective_at": "2026-11-04T00:00:00+00:00"})


condition = env.from_string(automation["conditions"][0]["value_template"])
for old, new, expected in [("30.00", "31.60", True), ("31.60", "30.00", True),
                           ("31.6", "31.60", False), ("unknown", "31.60", False),
                           ("unavailable", "31.60", False), ("31.60", "unavailable", False),
                           (None, "31.60", False), ("31.60", None, False)]:
    trigger = SimpleNamespace(from_state=state(old) if old is not None else None,
                              to_state=state(new) if new is not None else None,
                              entity_id="sensor.fuel_sa_reef_diesel_50_ppm")
    assert (condition.render(trigger=trigger).strip() == "True") == expected
    if expected:
        message = env.from_string(automation["actions"][0]["data"]["message"]).render(trigger=trigger)
        assert "160.00 cents" in message and "wholesale" in message
        assert ("increased" if float(new) > float(old) else "decreased") in message

assert automation["triggers"][0]["to"] is None
assert len(automation["triggers"][0]["entity_id"]) == 10
assert set(card["entity_id"]) == set(automation["triggers"][0]["entity_id"])
env.globals.update(states=lambda entity: "31.6", state_attr=lambda entity, attr: "2026-11-04T00:00:00+00:00")
rendered = env.from_string(card["content"]).render()
table_html = rendered[rendered.index('<table'):rendered.index('</table>') + len('</table>')]
table = ElementTree.fromstring(table_html)
assert table.attrib["width"] == "100%"
assert len(table.findall("thead/tr/th")) == 3
assert len(table.findall("tbody/tr")) == 5
assert all(len(row.findall("td")) == 3 for row in table.findall("tbody/tr"))
assert rendered.count("R31.60") == 10
assert "**Effective:** 04 Nov 2026" in rendered
assert "**Price effective dates**" not in rendered
env.globals["state_attr"] = lambda entity, attr: "2026-11-05T00:00:00+00:00" if entity.endswith("diesel_50_ppm") else "2026-11-04T00:00:00+00:00"
mixed = env.from_string(card["content"]).render()
assert "**Price effective dates**" in mixed and "05 Nov 2026" in mixed
assert mixed.count('<br>') >= 10
env.globals["states"] = lambda entity: "unavailable"
assert env.from_string(card["content"]).render().count("Unavailable") == 10

for file in (ROOT / "examples/www/fuelsa").glob("*.png"):
    image = Image.open(file)
    assert image.mode == "RGBA", image.mode
    alpha = image.getchannel("A")
    assert alpha.getextrema() == (0, 255)
    assert alpha.getpixel((image.width - 1, 0)) == 0
print("PASS: YAML, eight transition cases, message direction and amounts, table rows, unavailable states, and logo alpha.")
