from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    fieldsets = (
        (
            'Individuelle Daten',
            {
                'fields': (
                    'custom',
                    'phone',
                    'address',
                )
            }
        ),
        *UserAdmin.fieldsets,
    )
