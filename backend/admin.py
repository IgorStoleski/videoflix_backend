from django.contrib import admin
from .models import Video
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class VideoResources(resources.ModelResource):
    class Meta:
        model = Video
        """ fields = {'title', 'created_at', 'description'} """


@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    pass

