from django import forms

from .models import UserProfile


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
