from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "employee",
        "attendance_date",
        "check_in",
        "check_out",
        "status",
    )

    list_filter = (
        "status",
        "attendance_date",
    )

    search_fields = (
        "employee__name",
        "employee__email",
    )

    ordering = ("-attendance_date",)
