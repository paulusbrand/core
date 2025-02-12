"""IMGW-PIB sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from imgw_pib.model import HydrologicalData

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ImgwPibConfigEntry
from .const import ATTRIBUTION
from .coordinator import ImgwPibDataUpdateCoordinator

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class ImgwPibSensorEntityDescription(SensorEntityDescription):
    """IMGW-PIB sensor entity description."""

    value: Callable[[HydrologicalData], StateType]


SENSOR_TYPES: tuple[ImgwPibSensorEntityDescription, ...] = (
    ImgwPibSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value=lambda data: data.water_level.value,
    ),
    ImgwPibSensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value=lambda data: data.water_temperature.value,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ImgwPibConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a IMGW-PIB sensor entity from a config_entry."""
    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        ImgwPibSensorEntity(coordinator, description)
        for description in SENSOR_TYPES
        if getattr(coordinator.data, description.key).value is not None
    )


class ImgwPibSensorEntity(
    CoordinatorEntity[ImgwPibDataUpdateCoordinator], SensorEntity
):
    """Define IMGW-PIB sensor entity."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    entity_description: ImgwPibSensorEntityDescription

    def __init__(
        self,
        coordinator: ImgwPibDataUpdateCoordinator,
        description: ImgwPibSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{coordinator.station_id}_{description.key}"
        self._attr_device_info = coordinator.device_info
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self.entity_description.value(self.coordinator.data)
