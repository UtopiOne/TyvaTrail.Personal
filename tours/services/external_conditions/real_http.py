from __future__ import annotations

from typing import Any, Optional

import math
import requests

from .provider import DrivingLeg, WeatherNow, PlaceInfo


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


class RealHttpExternalConditionsProvider:

    name = "real_http"

    def __init__(self, *, timeout_s: int = 8) -> None:
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TyvaTrail/1.0 (external conditions)"
        })

    def driving_leg(self, lat1: float, lon1: float, lat2: float, lon2: float) -> DrivingLeg:
        try:
            url = (
                "https://router.project-osrm.org/route/v1/driving/"
                f"{lon1},{lat1};{lon2},{lat2}"
            )
            r = self.session.get(url, params={"overview": "false"}, timeout=self.timeout_s)
            r.raise_for_status()
            data: dict[str, Any] = r.json()
            route = (data.get("routes") or [None])[0]
            if route:
                dist_m = float(route.get("distance") or 0.0)
                dur_s = float(route.get("duration") or 0.0)
                return DrivingLeg(distance_km=dist_m / 1000.0, duration_min=int(round(dur_s / 60.0)))
        except Exception:
            pass

        km = _haversine_km(lat1, lon1, lat2, lon2) * 1.25
        return DrivingLeg(distance_km=km, duration_min=int(max(1, round(km))))

    def weather_now(self, lat: float, lon: float) -> WeatherNow:
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m",
                "timezone": "auto",
            }
            r = self.session.get(url, params=params, timeout=self.timeout_s)
            r.raise_for_status()
            data: dict[str, Any] = r.json()
            cur = data.get("current") or {}
            t = cur.get("temperature_2m")
            w = cur.get("wind_speed_10m")

            return WeatherNow(
                temperature_c=float(t) if t is not None else None,
                wind_speed_ms=(float(w) / 3.6) if w is not None else None,  # open-meteo часто даёт км/ч
            )
        except Exception:
            return WeatherNow()

    def place_info(self, lat: float, lon: float) -> PlaceInfo:
        try:
            url = "https://overpass-api.de/api/interpreter"
            query = f"""[out:json][timeout:10];
(
  node(around:200,{lat},{lon})[opening_hours];
  way(around:200,{lat},{lon})[opening_hours];
  relation(around:200,{lat},{lon})[opening_hours];
);
out tags 1;
"""
            r = self.session.post(url, data=query.encode("utf-8"), timeout=self.timeout_s)
            r.raise_for_status()
            data: dict[str, Any] = r.json()
            els = data.get("elements") or []
            if els:
                tags = (els[0].get("tags") or {})
                oh = tags.get("opening_hours")
                return PlaceInfo(opening_hours=str(oh) if oh else None)
        except Exception:
            pass
        return PlaceInfo()

    def get_conditions(self, route, points) -> dict[str, Any]:
        items: list[dict[str, Any]] = []

        for p in points:
            poi = getattr(p, "poi", None)
            lat = getattr(poi, "latitude", None) if poi else None
            lon = getattr(poi, "longitude", None) if poi else None

            weather = WeatherNow()
            place = PlaceInfo()

            if lat is not None and lon is not None:
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    weather = self.weather_now(lat_f, lon_f)
                    place = self.place_info(lat_f, lon_f)
                except Exception:
                    pass

            items.append({
                "point": p,
                "weather": weather,
                "place": place,
            })

        return {
            "provider": self.name,
            "points": items,
        }
