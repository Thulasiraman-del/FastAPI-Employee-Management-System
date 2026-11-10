from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance

User = get_user_model()


class ReportsAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="reportadmin",
            email="reportadmin@example.com",
            password="ReportAdminPassword123!",
        )

        self.department = Department.objects.create(
            name="Reports",
            code="RPT",
        )

        self.employee = Employee.objects.create(
            name="Report Employee",
            email="report.employee@example.com",
            phone="+919876543211",
            position="Analyst",
            salary=32000,
            department=self.department,
        )

    def test_dashboard_returns_statistics(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/reports/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_employees"], 1)
        self.assertEqual(response.data["total_departments"], 1)

    def test_employee_csv_export(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/reports/exports/employees/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("Report Employee", response.content.decode())
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_employee_csv_formula_injection_is_neutralized(self):
        self.employee.name = "=HYPERLINK(""https://example.com"",""Click"")"
        self.employee.save(update_fields=["name"])

        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/reports/exports/employees/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "'=HYPERLINK",
            response.content.decode(),
        )

    def test_attendance_csv_export(self):
        Attendance.objects.create(
            employee=self.employee,
            attendance_date=date(2026, 12, 1),
            notes="Normal attendance",
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/reports/exports/attendance/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("Normal attendance", response.content.decode())

    def test_employee_cannot_access_dashboard(self):
        employee_user = User.objects.create_user(
            username="reportemployee",
            email=self.employee.email,
            password="EmployeePassword123!",
        )

        self.client.force_authenticate(user=employee_user)
        response = self.client.get("/api/reports/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_export_employee_csv(self):
        employee_user = User.objects.create_user(
            username="reportemployee",
            email=self.employee.email,
            password="EmployeePassword123!",
        )

        self.client.force_authenticate(user=employee_user)
        response = self.client.get("/api/reports/exports/employees/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
