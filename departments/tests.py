from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department

User = get_user_model()


class DepartmentAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="departmentadmin",
            email="departmentadmin@example.com",
            password="DepartmentAdminPassword123!",
        )
        self.client.force_authenticate(user=self.admin)

    def test_admin_can_create_department(self):
        response = self.client.post(
            "/api/departments/",
            {
                "name": "Engineering",
                "code": "ENG",
                "description": "Engineering department",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Engineering")

    def test_department_name_is_trimmed(self):
        response = self.client.post(
            "/api/departments/",
            {"name": "  Finance  ", "code": "FIN"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Finance")

    def test_department_code_is_normalized(self):
        response = self.client.post(
            "/api/departments/",
            {"name": "Human Resources", "code": " hr "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], "HR")

    def test_duplicate_department_name_is_rejected_case_insensitively(self):
        Department.objects.create(name="Engineering", code="ENG")

        response = self.client.post(
            "/api/departments/",
            {"name": "engineering", "code": "ENG2"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_department_code_is_rejected_case_insensitively(self):
        Department.objects.create(name="Engineering", code="ENG")

        response = self.client.post(
            "/api/departments/",
            {"name": "Engineering Two", "code": "eng"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_whitespace_only_department_name_is_rejected(self):
        response = self.client.post(
            "/api/departments/",
            {"name": "   ", "code": "EMPTY"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
