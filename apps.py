from django.apps import AppConfig


class AdminBaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "admin_base"
