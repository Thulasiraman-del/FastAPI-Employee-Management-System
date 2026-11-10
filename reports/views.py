import csv
import io

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes

from accounts.permissions import IsAdminOrHR
from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leave_management.models import LeaveRequest


def safe_csv_text(value):
    """
    Protect spreadsheet users from CSV formula injection.
    Apply this to untrusted text fields, not numeric values.
    """
    value = "" if value is None else str(value)

    if value.lstrip(" \t\r\n\x00").startswith(("=", "+", "-", "@")):
        return "'" + value

    return value


def csv_response(filename):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


class DashboardView(APIView):
    permission_classes = [IsAdminOrHR]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        today = timezone.localdate()

        data = {
            "total_employees": Employee.objects.count(),
            "active_employees": Employee.objects.filter(is_active=True).count(),
            "inactive_employees": Employee.objects.filter(is_active=False).count(),
            "total_departments": Department.objects.count(),
            "active_departments": Department.objects.filter(is_active=True).count(),
            "attendance_today": Attendance.objects.filter(
                attendance_date=today
            ).count(),
            "present_today": Attendance.objects.filter(
                attendance_date=today,
                status=Attendance.Status.PRESENT,
            ).count(),
            "pending_leave_requests": LeaveRequest.objects.filter(
                status=LeaveRequest.Status.PENDING
            ).count(),
            "approved_leave_requests": LeaveRequest.objects.filter(
                status=LeaveRequest.Status.APPROVED
            ).count(),
            "rejected_leave_requests": LeaveRequest.objects.filter(
                status=LeaveRequest.Status.REJECTED
            ).count(),
        }

        return Response(data)


class EmployeeCSVExportView(APIView):
    permission_classes = [IsAdminOrHR]

    @extend_schema(responses={(200, "text/csv"): OpenApiTypes.BINARY})
    def get(self, request):
        response = csv_response("employees.csv")
        writer = csv.writer(response)

        writer.writerow([
            "ID", "Name", "Email", "Phone",
            "Position", "Salary", "Department", "Active",
        ])

        employees = Employee.objects.select_related("department").all()

        for employee in employees:
            writer.writerow([
                employee.id,
                safe_csv_text(employee.name),
                safe_csv_text(employee.email),
                safe_csv_text(employee.phone),
                safe_csv_text(employee.position),
                employee.salary,
                safe_csv_text(employee.department.name),
                employee.is_active,
            ])

        return response


class AttendanceCSVExportView(APIView):
    permission_classes = [IsAdminOrHR]

    @extend_schema(responses={(200, "text/csv"): OpenApiTypes.BINARY})
    def get(self, request):
        response = csv_response("attendance.csv")
        writer = csv.writer(response)

        writer.writerow([
            "ID", "Employee", "Date", "Check In",
            "Check Out", "Status", "Notes",
        ])

        records = Attendance.objects.select_related("employee").all()

        for record in records:
            writer.writerow([
                record.id,
                safe_csv_text(record.employee.name),
                record.attendance_date,
                record.check_in,
                record.check_out,
                record.status,
                safe_csv_text(record.notes),
            ])

        return response
