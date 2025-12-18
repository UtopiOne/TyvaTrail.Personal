from __future__ import annotations

from django.utils import timezone
from .provider import DrivingLeg, ExternalConditionsProvider, WeatherNow, PlaceInfo
from ..geo import haversine_km

class StubExternalConditionsProvider(ExternalConditionsProvider):
    def __init__(self, avg_speed_kmh: float = 60.0):
        self.avg_speed_kmh = avg_speed_kmh

    def driving_leg(self, lat1: float, lon1: float, lat2: float, lon2: float) -> DrivingLeg:
        km = haversine_km(lat1, lon1, lat2, lon2)
        minutes = int(round((km / self.avg_speed_kmh) * 60.0))
        return DrivingLeg(distance_km=float(km), duration_min=max(0, minutes), source="stub:haversine")

    def weather_now(self, lat: float, lon: float, tz: str) -> WeatherNow:
        return WeatherNow(temperature_c=None, wind_speed_ms=None, weather_code=None, source="stub:none")

    def place_info(self, lat: float, lon: float, name: str, radius_m: int = 1500) -> PlaceInfo:
        return PlaceInfo(opening_hours=None, source="stub:none")

    def get_conditions(self, *, route, points, tz: str | None = None) -> dict:
        tz = tz or timezone.get_current_timezone_name()

        points_ctx = []
        legs_ctx = []
        prev_by_day = {}

        for rp in points:
            poi = rp.poi
            lat = getattr(poi, "latitude", None)
            lon = getattr(poi, "longitude", None)

            if lat is not None and lon is not None:
                lat_f, lon_f = float(lat), float(lon)
                weather = self.weather_now(lat_f, lon_f, tz)
                place = self.place_info(lat_f, lon_f, poi.name)
            else:
                weather = WeatherNow(None, None, None, "no-coords")
                place = PlaceInfo(None, "no-coords")

            points_ctx.append({"point": rp, "weather": weather, "place": place})

            day = getattr(rp, "day_number", None)
            prev = prev_by_day.get(day)
            if prev is not None:
                ppoi = prev.poi
                lat1, lon1 = getattr(ppoi, "latitude", None), getattr(ppoi, "longitude", None)
                if None not in (lat1, lon1, lat, lon):
                    leg = self.driving_leg(float(lat1), float(lon1), float(lat), float(lon))
                    legs_ctx.append({"day": day, "from_point": prev, "to_point": rp, "leg": leg})

            prev_by_day[day] = rp

        return {"points": points_ctx, "legs": legs_ctx, "provider": "stub"}