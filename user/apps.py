from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'

    def ready(self):
        from django.contrib import admin
        from rest_framework.authtoken.models import Token
        try:
            admin.site.unregister(Token)
        except admin.sites.NotRegistered:
            pass