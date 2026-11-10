from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department
from employees.models import Employee
from leave_management.models import LeaveRequest

User = get_user_model()


class RolePermissionTests(APITestCase):

    def setUp(self):
        self.hr = User.objects.create_user(
            username="permission_hr",
            email="permission_hr@example.com",
            password="StrongTestPassword123!",
            role="HR",
        )

        self.employee_user = User.objects.create_user(
            username="permission_employee",
            email="permission_employee@example.com",
            password="StrongTestPassword123!",
            role="EMPLOYEE",
        )

        self.department = Department.objects.create(
            name="Permission Testing",
            code="PERM",
        )

        self.employee = Employee.objects.create(
            name="Permission Employee",
            email=self.employee_user.email,
            phone="+919876543210",
            position="Developer",
            salary=30000,
            department=self.department,
        )

    def test_employee_cannot_read_administrative_apis(self):
        self.client.force_authenticate(user=self.employee_user)

        endpoints = [
            "/api/departments/",
            "/api/employees/",
            "/api/attendance/",
            "/api/reports/dashboard/",
            "/api/reports/exports/employees/",
            "/api/reports/exports/attendance/",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                    f"Employee unexpectedly accessed {endpoint}",
                )

    def test_employee_cannot_create_department(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.post(
            "/api/departments/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_hr_can_read_administrative_apis(self):
        self.client.force_authenticate(user=self.hr)

        endpoints = [
            "/api/departments/",
            "/api/employees/",
            "/api/attendance/",
            "/api/reports/dashboard/",
            "/api/reports/exports/employees/",
            "/api/reports/exports/attendance/",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    f"HR could not access {endpoint}: status={response.status_code}, content_type={response.get('Content-Type')}",
                )

    def test_employee_only_sees_own_leave_requests(self):
        another_employee = Employee.objects.create(
            name="Another Employee",
            email="another.employee@example.com",
            phone="+919876543211",
            position="Tester",
            salary=28000,
            department=self.department,
        )

        own_leave = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 2),
            reason="Personal appointment",
        )

        LeaveRequest.objects.create(
            employee=another_employee,
            start_date=date(2026, 12, 3),
            end_date=date(2026, 12, 4),
            reason="Personal work",
        )

        self.client.force_authenticate(user=self.employee_user)

        response = self.client.get("/api/leave-requests/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            own_leave.id,
        )

    def test_employee_cannot_approve_leave_request(self):
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2026, 12, 5),
            end_date=date(2026, 12, 6),
            reason="Personal work",
        )

        self.client.force_authenticate(user=self.employee_user)

        response = self.client.post(
            f"/api/leave-requests/{leave.id}/approve/",
            {"review_comments": "Approved"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveRequest.Status.PENDING)
