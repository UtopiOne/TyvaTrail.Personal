from __future__ import annotations

from django.db.models import (
    Q, Case, When, Value, IntegerField, F, ExpressionWrapper,
)
from django.db.models.functions import Coalesce

from ..models import (
    Season,
    PhysicalLevel,
    PriceLevel,
    TravelStyle,
    PoiType,
)


STYLE_TO_TYPES: dict[str, list[str]] = {
    TravelStyle.ACTIVE: [PoiType.NATURE, PoiType.OTHER],
    TravelStyle.CULTURAL: [PoiType.CULTURE, PoiType.MUSEUM],
    TravelStyle.RELAX: [PoiType.GUESTHOUSE, PoiType.FOOD],
    TravelStyle.MIXED: [],
}

PHYSICAL_ALLOWED: dict[str, list[str]] = {
    PhysicalLevel.EASY: [PhysicalLevel.EASY],
    PhysicalLevel.MEDIUM: [PhysicalLevel.EASY, PhysicalLevel.MEDIUM],
    PhysicalLevel.HARD: [PhysicalLevel.EASY, PhysicalLevel.MEDIUM, PhysicalLevel.HARD],
}


def _interest_q(interests: str | None) -> Q | None:
    if not interests:
        return None
    raw = [t.strip() for t in interests.replace(",", " ").split()]
    tokens = [t for t in raw if len(t) >= 3][:3]
    if not tokens:
        return None

    q = Q()
    for t in tokens:
        q |= (
            Q(name__icontains=t)
            | Q(short_description__icontains=t)
            | Q(detailed_description__icontains=t)
            | Q(region__icontains=t)
        )
    return q


def apply_profile_preferences(qs, profile):
    qs = qs.filter(season__in=[profile.preferred_season, Season.YEAR_ROUND])

    allowed = PHYSICAL_ALLOWED.get(profile.physical_level, PHYSICAL_ALLOWED[PhysicalLevel.MEDIUM])
    if profile.with_children:
        allowed = [PhysicalLevel.EASY]
    qs = qs.filter(physical_level__in=allowed)

    if profile.budget_level == PriceLevel.LOW:
        qs = qs.filter(price_level__in=[PriceLevel.LOW, PriceLevel.MEDIUM])

    preferred_types = STYLE_TO_TYPES.get(profile.travel_style, [])
    style_score = (
        Case(
            When(type__in=preferred_types, then=Value(3)),
            default=Value(0),
            output_field=IntegerField(),
        )
        if preferred_types
        else Value(0, output_field=IntegerField())
    )

    interest_q = _interest_q(profile.interests)
    interest_score = (
        Case(
            When(interest_q, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        if interest_q
        else Value(0, output_field=IntegerField())
    )

    qs = qs.annotate(rating0=Coalesce("avg_rating", Value(0.0)))

    qs = qs.annotate(
        style_score=style_score,
        interest_score=interest_score,
    ).annotate(
        pref_score=ExpressionWrapper(
            F("style_score") + F("interest_score"),
            output_field=IntegerField(),
        )
    )

    return qs.order_by("-pref_score", "-rating0", "base_cost", "name")
