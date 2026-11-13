"""Price sensors discovered from the current feed."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    """Discover new grades after updates as well as at startup."""
    coordinator = entry.runtime_data
    known = set()

    @callback
    def discover():
        new = set(coordinator.data) - known
        async_add_entities(FuelSAPriceSensor(coordinator, key) for key in sorted(new))
        known.update(new)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class FuelSAPriceSensor(CoordinatorEntity, SensorEntity):
    """A price in South African rand per litre."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "ZAR/L"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:gas-station"
    _attr_attribution = "Data provided by Fuel SA"

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self.key = key
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_name = coordinator.data[key].name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)}, name="Fuel SA",
            manufacturer="Fuel SA", entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.fuelsa.co.za/",
        )

    @property
    def available(self):
        return super().available and self.key in self.coordinator.data

    @property
    def native_value(self):
        item = self.coordinator.data.get(self.key)
        return item.price if item else None

    @property
    def extra_state_attributes(self):
        if (item := self.coordinator.data.get(self.key)) is None:
            return {}
        return {"location": item.location, "fuel": item.fuel, "grade": item.grade,
                "effective_at": item.effective_at.isoformat(),
                "price_basis": "wholesale" if item.fuel == "diesel" else "retail"}
