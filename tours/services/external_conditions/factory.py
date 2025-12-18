from __future__ import annotations

from django.conf import settings

from .stub import StubExternalConditionsProvider

try:
    from .real_http import RealHttpExternalConditionsProvider
except Exception:
    RealHttpExternalConditionsProvider = None


def get_external_conditions_provider():
    raw = getattr(settings, "EXTERNAL_CONDITIONS_PROVIDER", "") or ""
    key = raw.strip().lower()

    if key in {"real_http", "realhttp", "real"} and RealHttpExternalConditionsProvider is not None:
        return RealHttpExternalConditionsProvider()

    return StubExternalConditionsProvider()
