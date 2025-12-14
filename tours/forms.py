from django import forms

from .models import Review
from .models import UserProfile
from .models import PoiType, Season, PriceLevel, PhysicalLevel


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "travel_style",
            "budget_level",
            "physical_level",
            "preferred_season",
            "with_children",
            "interests",
            "notes",
        ]


class RouteRequestForm(forms.Form):
    days_count = forms.IntegerField(
        label="Длительность поездки (дней)",
        min_value=1,
        max_value=30,
        initial=3,
    )
    max_budget = forms.IntegerField(
        label="Ориентировочный бюджет (₽)",
        required=False,
        min_value=0,
    )


class PoiFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Поиск")
    type = forms.ChoiceField(required=False, choices=[("", "Все")] + list(PoiType.choices), label="Тип")
    region = forms.CharField(required=False, label="Регион / район")
    season = forms.ChoiceField(required=False, choices=[("", "Все")] + list(Season.choices), label="Сезон")
    price_level = forms.ChoiceField(required=False, choices=[("", "Все")] + list(PriceLevel.choices), label="Уровень цен")
    physical_level = forms.ChoiceField(required=False, choices=[("", "Все")] + list(PhysicalLevel.choices), label="Сложность")


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        label="Оценка",
        choices=[(i, str(i)) for i in range(1, 6)],
        coerce=int,
        empty_value=None,
    )

    class Meta:
        model = Review
        fields = ["rating", "text"]
        labels = {"text": "Текст отзыва"}

