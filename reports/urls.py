from django.urls import path
from .views import (
    DashboardView,
    EmployeeCSVExportView,
    AttendanceCSVExportView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("exports/employees/", EmployeeCSVExportView.as_view(), name="export-employees"),
    path("exports/attendance/", AttendanceCSVExportView.as_view(), name="export-attendance"),
]
