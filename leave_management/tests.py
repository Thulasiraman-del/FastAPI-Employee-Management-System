from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department
from employees.models import Employee
from leave_management.models import LeaveRequest

User = get_user_model()


class LeaveRequestAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="testadmin",
            email="testadmin@example.com",
            password="TestAdminPassword123!",
        )

        self.department = Department.objects.create(
            name="Testing",
            code="TST",
        )

        self.employee = Employee.objects.create(
            name="Test Employee",
            email="employee@example.com",
            phone="+919876543210",
            position="Developer",
            salary=30000,
            department=self.department,
        )

    def create_leave(self, start_day=1, end_day=2):
        return LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2026, 12, start_day),
            end_date=date(2026, 12, end_day),
            reason="Personal work",
        )

    def test_admin_can_create_leave_request(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/leave-requests/",
            {
                "employee": self.employee.id,
                "start_date": "2026-12-01",
                "end_date": "2026-12-03",
                "reason": "Personal work",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")
        self.assertEqual(response.data["leave_days"], 3)

    def test_invalid_date_range_is_rejected(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/leave-requests/",
            {
                "employee": self.employee.id,
                "start_date": "2026-12-05",
                "end_date": "2026-12-01",
                "reason": "Personal work",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_approve_leave(self):
        leave = self.create_leave()

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/approve/",
            {"review_comments": "Approved"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveRequest.Status.APPROVED)
        self.assertEqual(leave.reviewed_by, self.admin)
        self.assertIsNotNone(leave.reviewed_at)

    def test_admin_can_reject_leave(self):
        leave = self.create_leave(5, 6)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/reject/",
            {"review_comments": "Insufficient staffing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveRequest.Status.REJECTED)

    def test_employee_can_apply_without_sending_employee_id(self):
        employee_user = User.objects.create_user(
            username="employeeuser",
            email=self.employee.email,
            password="EmployeePassword123!",
        )

        self.client.force_authenticate(user=employee_user)
        response = self.client.post(
            "/api/leave-requests/",
            {
                "start_date": "2026-12-10",
                "end_date": "2026-12-11",
                "reason": "Personal appointment",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["employee"], self.employee.id)

    def test_employee_can_only_see_own_leave_requests(self):
        other_employee = Employee.objects.create(
            name="Other Employee",
            email="other@example.com",
            phone="+919876543213",
            position="Analyst",
            salary=25000,
            department=self.department,
        )

        own_leave = self.create_leave()
        LeaveRequest.objects.create(
            employee=other_employee,
            start_date=date(2026, 12, 5),
            end_date=date(2026, 12, 6),
            reason="Other employee leave",
        )

        employee_user = User.objects.create_user(
            username="employeeuser",
            email=self.employee.email,
            password="EmployeePassword123!",
        )

        self.client.force_authenticate(user=employee_user)
        response = self.client.get("/api/leave-requests/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], own_leave.id)

    def test_employee_cannot_approve_leave(self):
        leave = self.create_leave()

        employee_user = User.objects.create_user(
            username="employeeuser",
            email=self.employee.email,
            password="EmployeePassword123!",
        )

        self.client.force_authenticate(user=employee_user)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/approve/",
            {"review_comments": "Approved"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_string_review_comments_are_rejected(self):
        leave = self.create_leave()

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/reject/",
            {"review_comments": ["invalid", "list"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveRequest.Status.PENDING)

    def test_review_comments_over_2000_characters_are_rejected(self):
        leave = self.create_leave()

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/reject/",
            {"review_comments": "A" * 2001},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveRequest.Status.PENDING)

    def test_approval_trims_review_comments(self):
        leave = self.create_leave()

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/approve/",
            {"review_comments": "  Approved  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave.refresh_from_db()
        self.assertEqual(leave.review_comments, "Approved")

    def test_reviewing_already_reviewed_leave_is_rejected(self):
        leave = self.create_leave()
        leave.status = LeaveRequest.Status.APPROVED
        leave.save(update_fields=["status"])

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/leave-requests/{leave.id}/reject/",
            {"review_comments": "Reject"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
