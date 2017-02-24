from django.contrib import admin

from board import models


@admin.register(models.Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    ordering = ['name']


@admin.register(models.VerifType)
class VerifTypeAdmin(admin.ModelAdmin):
    pass


class VerifValueInline(admin.TabularInline):
    model = models.VerifValue


@admin.register(models.Verif)
class VerifAdmin(admin.ModelAdmin):
    inlines = [
        VerifValueInline
    ]

    list_display = ['tag', 'type', 'display_name', 'icon', 'mandatory']

    list_display_links = ['tag']
    list_editable = ['display_name', 'icon', 'mandatory']

    list_filter = ['type', 'mandatory']


@admin.register(models.VerifValue)
class VerifValueAdmin(admin.ModelAdmin):
    list_display = ['id', 'verif', 'value']
    list_display_links = ['id']
    list_editable = ['verif', 'value']
