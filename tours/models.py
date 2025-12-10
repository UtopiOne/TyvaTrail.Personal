from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class PoiType(models.TextChoices):
    NATURE = "NATURE", "Природный объект"
    CULTURE = "CULTURE", "Культурный объект"
    MUSEUM = "MUSEUM", "Музей"
    GUESTHOUSE = "GUESTHOUSE", "Гостевой дом / база"
    SHAMAN_CLINIC = "SHAMAN_CLINIC", "Шаманская клиника"
    FOOD = "FOOD", "Кафе / ресторан"
    OTHER = "OTHER", "Другое"


class Season(models.TextChoices):
    YEAR_ROUND = "YEAR_ROUND", "Круглый год"
    SPRING = "SPRING", "Весна"
    SUMMER = "SUMMER", "Лето"
    AUTUMN = "AUTUMN", "Осень"
    WINTER = "WINTER", "Зима"


class PriceLevel(models.TextChoices):
    LOW = "LOW", "Низкий"
    MEDIUM = "MEDIUM", "Средний"
    HIGH = "HIGH", "Высокий"


class PhysicalLevel(models.TextChoices):
    EASY = "EASY", "Лёгкий"
    MEDIUM = "MEDIUM", "Средний"
    HARD = "HARD", "Сложный"


class TravelStyle(models.TextChoices):
    ACTIVE = "ACTIVE", "Активный"
    CULTURAL = "CULTURAL", "Культурно-познавательный"
    RELAX = "RELAX", "Релакс / отдых"
    MIXED = "MIXED", "Смешанный"


class Poi(models.Model):
    name = models.CharField("Название", max_length=255)
    short_description = models.TextField("Краткое описание")
    detailed_description = models.TextField("Подробное описание", blank=True)

    type = models.CharField("Тип объекта", max_length=20, choices=PoiType.choices)
    region = models.CharField("Регион / район", max_length=255, blank=True)

    latitude = models.DecimalField(
        "Широта", max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        "Долгота", max_digits=9, decimal_places=6, null=True, blank=True
    )

    address = models.CharField("Адрес / точка въезда", max_length=255, blank=True)
    access_info = models.TextField("Как добраться / дорога", blank=True)

    visit_duration_hours = models.DecimalField(
        "Время на посещение (часы)", max_digits=4, decimal_places=1, default=2.0
    )

    physical_level = models.CharField(
        "Физическая сложность",
        max_length=20,
        choices=PhysicalLevel.choices,
        default=PhysicalLevel.MEDIUM,
    )

    season = models.CharField(
        "Сезон доступности",
        max_length=20,
        choices=Season.choices,
        default=Season.YEAR_ROUND,
    )

    price_level = models.CharField(
        "Уровень цен", max_length=20, choices=PriceLevel.choices
    )
    base_cost = models.PositiveIntegerField(
        "Ориентировочная стоимость (₽)", null=True, blank=True
    )

    image_url = models.URLField("Ссылка на фотографию", blank=True)

    avg_rating = models.FloatField("Средний рейтинг", null=True, blank=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Объект (POI)"
        verbose_name_plural = "Объекты (POI)"

    def __str__(self):
        return self.name


class PoiPhoto(models.Model):

    poi = models.ForeignKey(
        Poi,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Объект",
    )
    image_url = models.URLField("Ссылка на фото")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "Фото объекта"
        verbose_name_plural = "Фотографии объектов"

    def __str__(self):
        return f"Фото {self.poi.name}"


class UserProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    travel_style = models.CharField(
        "Стиль путешествия",
        max_length=20,
        choices=TravelStyle.choices,
        default=TravelStyle.MIXED,
    )
    budget_level = models.CharField(
        "Уровень бюджета",
        max_length=20,
        choices=PriceLevel.choices,
        default=PriceLevel.MEDIUM,
    )
    physical_level = models.CharField(
        "Физподготовка",
        max_length=20,
        choices=PhysicalLevel.choices,
        default=PhysicalLevel.MEDIUM,
    )
    preferred_season = models.CharField(
        "Предпочитаемый сезон",
        max_length=20,
        choices=Season.choices,
        default=Season.SUMMER,
    )
    with_children = models.BooleanField("С детьми", default=False)
    interests = models.TextField("Интересы (шаманизм, археология...)", blank=True)
    notes = models.TextField("Особые пожелания / ограничения", blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.username}"


class Route(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="routes",
    )
    name = models.CharField("Название маршрута", max_length=255)
    days_count = models.PositiveIntegerField("Кол-во дней", default=1)
    total_duration_hours = models.PositiveIntegerField("Общее время (часы)", default=0)
    total_cost = models.PositiveIntegerField(
        "Ориентировочная стоимость (₽)", null=True, blank=True
    )
    equipment = models.TextField("Необходимая экипировка", blank=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class RoutePoint(models.Model):

    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="points", verbose_name="Маршрут"
    )
    poi = models.ForeignKey(Poi, on_delete=models.CASCADE, verbose_name="Объект")
    day_number = models.PositiveIntegerField("День", default=1)
    order_index = models.PositiveIntegerField("Порядок в дне", default=1)
    note = models.TextField("Примечание", blank=True)

    visit_time_estimate = models.DecimalField(
        "Планируемое время (часы)", max_digits=4, decimal_places=1, default=2.0
    )

    class Meta:
        verbose_name = "Точка маршрута"
        verbose_name_plural = "Точки маршрута"
        ordering = ["day_number", "order_index"]


class Review(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    poi = models.ForeignKey(
        Poi,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Объект",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка (1–5)",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField("Текст отзыва", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв {self.user.username} о {self.poi.name}"
