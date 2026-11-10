from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance

User = get_user_model()


class AttendanceAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="attendanceadmin",
            email="attendanceadmin@example.com",
            password="AttendanceAdminPassword123!",
        )

        self.department = Department.objects.create(
            name="Attendance Testing",
            code="ATT",
        )

        self.employee = Employee.objects.create(
            name="Attendance Employee",
            email="attendance.employee@example.com",
            phone="+919876543212",
            position="Developer",
            salary=30000,
            department=self.department,
        )

        self.client.force_authenticate(user=self.admin)

    def test_admin_can_create_attendance(self):
        response = self.client.post(
            "/api/attendance/",
            {
                "employee": self.employee.id,
                "attendance_date": "2026-12-01",
                "status": "PRESENT",
                "notes": "On time",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["employee_name"], "Attendance Employee")

    def test_check_out_before_check_in_is_rejected(self):
        response = self.client.post(
            "/api/attendance/",
            {
                "employee": self.employee.id,
                "attendance_date": "2026-12-02",
                "check_in": "2026-12-02T10:00:00+05:30",
                "check_out": "2026-12-02T09:00:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_equal_check_in_and_check_out_is_rejected(self):
        response = self.client.post(
            "/api/attendance/",
            {
                "employee": self.employee.id,
                "attendance_date": "2026-12-03",
                "check_in": "2026-12-03T10:00:00+05:30",
                "check_out": "2026-12-03T10:00:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_employee_attendance_for_same_date_is_rejected(self):
        Attendance.objects.create(
            employee=self.employee,
            attendance_date=date(2026, 12, 4),
        )

        response = self.client.post(
            "/api/attendance/",
            {
                "employee": self.employee.id,
                "attendance_date": "2026-12-04",
                "status": "PRESENT",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attendance_notes_are_trimmed(self):
        response = self.client.post(
            "/api/attendance/",
            {
                "employee": self.employee.id,
                "attendance_date": "2026-12-05",
                "notes": "  Worked remotely  ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["notes"], "Worked remotely")

    def test_employee_role_cannot_access_attendance_api(self):
        employee_user = User.objects.create_user(
            username="attendanceemployee",
            email=self.employee.email,
            password="EmployeePassword123!",
        )

        self.client.force_authenticate(user=employee_user)

        response = self.client.get("/api/attendance/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attendance_can_be_filtered_by_status(self):
        Attendance.objects.create(
            employee=self.employee,
            attendance_date=date(2026, 12, 6),
            status=Attendance.Status.PRESENT,
        )

        response = self.client.get("/api/attendance/?status=PRESENT")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
