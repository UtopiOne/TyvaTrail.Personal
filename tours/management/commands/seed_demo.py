from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tours.models import Poi, PoiPhoto, Route, RoutePoint, Review


class Command(BaseCommand):
    help = "Заполняет базу демо-данными для TyvaTrail (POI, маршрут, точки, отзывы)."

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()

        if not user:
            self.stdout.write(
                self.style.ERROR(
                    "В базе нет ни одного пользователя. "
                    "Сначала создай хотя бы суперпользователя (python manage.py createsuperuser)."
                )
            )
            return

        if Poi.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "В базе уже есть объекты POI. "
                    "Чтобы не плодить дубликаты, демо-данные не создаю."
                )
            )
            return

        self.stdout.write(self.style.NOTICE(f"Используем пользователя: {user}"))

        # --- создаём несколько POI ---

        poi_data = [
            {
                "name": "Озеро Чедер",
                "short_description": "Минеральное озеро, популярное место отдыха.",
                "detailed_description": "Лечебная вода, возможность купания, красивые виды.",
                "type": "NATURE",
                "region": "Тува, Чедер",
                "latitude": Decimal("51.666000"),
                "longitude": Decimal("95.000000"),
                "price_level": "MEDIUM",
                "base_cost": 500,
                "season": "SUMMER",
                "physical_level": "EASY",
                "visit_duration_hours": Decimal("3.0"),
                "image_url": "https://example.com/cheder.jpg",
            },
            {
                "name": "Национальный музей Республики Тыва",
                "short_description": "Крупнейший музей Тувы.",
                "detailed_description": (
                    "Экспозиции по истории, культуре, археологии региона."
                ),
                "type": "MUSEUM",
                "region": "Кызыл",
                "latitude": Decimal("51.720000"),
                "longitude": Decimal("94.450000"),
                "price_level": "LOW",
                "base_cost": 300,
                "season": "YEAR_ROUND",
                "physical_level": "EASY",
                "visit_duration_hours": Decimal("2.0"),
                "image_url": "https://example.com/museum.jpg",
            },
            {
                "name": "Шаманская клиника",
                "short_description": "Место для традиционных обрядов и практик.",
                "detailed_description": "Приём шаманов, ритуалы очищения, консультации.",
                "type": "SHAMAN_CLINIC",
                "region": "Окрестности Кызыла",
                "latitude": None,
                "longitude": None,
                "price_level": "HIGH",
                "base_cost": 5000,
                "season": "YEAR_ROUND",
                "physical_level": "EASY",
                "visit_duration_hours": Decimal("1.5"),
                "image_url": "https://example.com/shaman.jpg",
            },
        ]

        pois = []

        for data in poi_data:
            poi = Poi.objects.create(
                name=data["name"],
                short_description=data["short_description"],
                detailed_description=data["detailed_description"],
                type=data["type"],
                region=data["region"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                price_level=data["price_level"],
                base_cost=data["base_cost"],
                season=data["season"],
                physical_level=data["physical_level"],
                visit_duration_hours=data["visit_duration_hours"],
                image_url=data["image_url"],
            )
            pois.append(poi)
            self.stdout.write(self.style.SUCCESS(f"Создан POI: {poi}"))

        # --- дополнительные фото к POI ---

        PoiPhoto.objects.create(
            poi=pois[0],
            image_url="https://example.com/cheder_2.jpg",
            caption="Вид на озеро Чедер",
        )
        PoiPhoto.objects.create(
            poi=pois[1],
            image_url="https://example.com/museum_2.jpg",
            caption="Экспозиция музея",
        )
        self.stdout.write(self.style.SUCCESS("Добавлены дополнительные фото."))

        # --- создаём маршрут ---

        route = Route.objects.create(
            user=user,
            name="Тестовый маршрут: Кызыл и озеро Чедер",
            days_count=2,
            total_duration_hours=10,
            total_cost=8000,
            equipment="Удобная обувь, купальные принадлежности, ветровка.",
        )
        self.stdout.write(self.style.SUCCESS(f"Создан маршрут: {route}"))

        # --- точки маршрута ---

        RoutePoint.objects.create(
            route=route,
            poi=pois[1],  # музей
            day_number=1,
            order_index=1,
            visit_time_estimate=Decimal("2.0"),
            note="Утреннее посещение музея.",
        )

        RoutePoint.objects.create(
            route=route,
            poi=pois[2],  # шаманская клиника
            day_number=1,
            order_index=2,
            visit_time_estimate=Decimal("1.5"),
            note="Дневной визит к шаманам.",
        )

        RoutePoint.objects.create(
            route=route,
            poi=pois[0],  # озеро Чедер
            day_number=2,
            order_index=1,
            visit_time_estimate=Decimal("3.0"),
            note="Купание и отдых у озера.",
        )

        self.stdout.write(self.style.SUCCESS("Созданы точки маршрута."))

        # --- отзывы ---

        Review.objects.create(
            user=user,
            poi=pois[0],
            rating=5,
            text="Очень понравилось озеро, красивые виды и приятная вода.",
        )
        Review.objects.create(
            user=user,
            poi=pois[1],
            rating=4,
            text="Интересный музей, но хотелось бы больше интерактива.",
        )

        self.stdout.write(self.style.SUCCESS("Добавлены тестовые отзывы."))
        self.stdout.write(self.style.SUCCESS("Готово! Демо-данные созданы."))
