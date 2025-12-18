from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import Route, RoutePoint


@dataclass(frozen=True)
class DrivingLeg:
    distance_km: float
    duration_min: int


@dataclass(frozen=True)
class WeatherNow:
    temperature_c: Optional[float] = None
    wind_speed_ms: Optional[float] = None


@dataclass(frozen=True)
class PlaceInfo:
    opening_hours: Optional[str] = None


class ExternalConditionsProvider(Protocol):

    name: str

    def driving_leg(self, lat1: float, lon1: float, lat2: float, lon2: float) -> DrivingLeg: ...
    def weather_now(self, lat: float, lon: float) -> WeatherNow: ...
    def place_info(self, lat: float, lon: float) -> PlaceInfo: ...

    def get_conditions(self, route: "Route", points: list["RoutePoint"]) -> dict[str, Any]: ...
