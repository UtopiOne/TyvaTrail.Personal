from django import template

register = template.Library()


@register.filter
def minutes_human(value):
    if value is None:
        return ""
    try:
        m = int(round(float(value)))
    except (TypeError, ValueError):
        return ""
    h, mm = divmod(m, 60)
    return f"{h} ч {mm} мин" if h else f"{mm} мин"
