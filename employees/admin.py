from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "email",
        "position",
        "department",
        "salary",
        "is_active",
    )

    list_filter = (
        "department",
        "is_active",
    )

    search_fields = (
        "name",
        "email",
        "position",
    )

    ordering = ("id",)
