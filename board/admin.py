from django.contrib import admin

from board import models


@admin.register(models.Computer)
class ComputerAdmin(admin.ModelAdmin):
    pass
