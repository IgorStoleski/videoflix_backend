from django.contrib import admin
from .models import Video
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin


class VideoResources(resources.ModelResource):
    class Meta:
        model = Video


@admin.register(Video)
class VideoAdmin(ImportExportActionModelAdmin):
    """ list_display = ('title', 'created_at', 'description') """
    pass
