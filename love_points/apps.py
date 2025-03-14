from django.apps import AppConfig


class LovePointsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "love_points"

    def ready(self):
        import love_points.signals
