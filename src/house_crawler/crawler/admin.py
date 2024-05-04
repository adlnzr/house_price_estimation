from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Post, PostToken


class Admin(ImportExportModelAdmin, admin.ModelAdmin):
    list_filter = ['is_active', 'created_at']


class PostAdmin(Admin):
    list_display = ['token', 'city', 'title', 'price', 'has_map']

    def has_map(self, obj):
        return obj.latitude is not None


class PostTokenAdmin(Admin):
    list_display = ['code', 'is_active', ]


admin.site.register(Post, PostAdmin)
admin.site.register(PostToken, PostTokenAdmin)
