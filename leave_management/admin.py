from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "start_date",
        "end_date",
        "status",
        "reviewed_by",
        "applied_at",
    )
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("employee__name", "employee__email", "reason")
    readonly_fields = ("applied_at", "reviewed_at")
    ordering = ("-applied_at",)
