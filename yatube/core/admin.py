from django.contrib import admin

from .models import ObsceneWord


class ObseneWordAdmin(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ('word',)


admin.site.register(ObsceneWord, ObseneWordAdmin)
