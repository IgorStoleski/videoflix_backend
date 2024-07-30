from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import site
from rest_framework.authtoken.models import Token
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from rest_framework.authtoken.models import TokenProxy

admin.site.unregister(TokenProxy)


class CustomUserAdmin(UserAdmin):
    """
    A custom UserAdmin class that extends Django's UserAdmin to tailor the user management interface in the Django admin.
    Attributes:
        add_form (forms.ModelForm): The form used when creating a new user.
        form (forms.ModelForm): The form used for modifying an existing user.
        model (django.db.models.Model): The custom user model associated with this admin interface.
        list_display (tuple): Tuple of field names to display in the user list.
        list_filter (tuple): Tuple of field names to filter in the user list.
        fieldsets (tuple): Configuration of fields grouped together in sections for the user detail view.
        add_fieldsets (tuple): Configuration of fields grouped together in sections specifically for the add user view.
        search_fields (tuple): Tuple of field names that are searchable in the user list.
        ordering (tuple): Tuple of field names to determine the order of records in the user list.
    This class customizes the admin interface for the `CustomUser` model, providing specific settings for displaying,
    filtering, and editing user details in a structured and accessible format. It handles both creation and modification
    of user records.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password"),
                "classes": ("wide",)}),
        ("Personal info", {"fields": ("username", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "username",
                "first_name", "last_name", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
