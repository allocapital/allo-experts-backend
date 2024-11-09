from django.apps import AppConfig


class BuildsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'builds'

    def ready(self):
        import builds.signals