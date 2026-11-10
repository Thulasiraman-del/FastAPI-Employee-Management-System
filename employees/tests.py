from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department
from employees.models import Employee

User = get_user_model()


class EmployeeAPITests(APITestCase):

    def setUp(self):
        self.hr = User.objects.create_user(
            username="employee_test_hr",
            email="employee_test_hr@example.com",
            password="StrongTestPassword123!",
            role="HR",
        )

        self.employee_user = User.objects.create_user(
            username="employee_test_user",
            email="employee_test_user@example.com",
            password="StrongTestPassword123!",
            role="EMPLOYEE",
        )

        self.department = Department.objects.create(
            name="Employee API Testing",
            code="EAT",
        )

        self.employee = Employee.objects.create(
            name="Existing Employee",
            email="existing.employee@example.com",
            phone="+919876543210",
            position="Developer",
            salary=30000,
            department=self.department,
        )

        self.client.force_authenticate(user=self.hr)

    def valid_payload(self, **overrides):
        payload = {
            "name": "New Employee",
            "email": "new.employee@example.com",
            "phone": "+919876543211",
            "position": "Backend Developer",
            "salary": "35000.00",
            "department": self.department.id,
        }
        payload.update(overrides)
        return payload

    def test_hr_can_create_employee(self):
        response = self.client.post(
            "/api/employees/",
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["email"],
            "new.employee@example.com",
        )

    def test_email_is_normalized_to_lowercase(self):
        response = self.client.post(
            "/api/employees/",
            self.valid_payload(email="  NEW.USER@EXAMPLE.COM  "),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "new.user@example.com")

    def test_duplicate_email_is_rejected_case_insensitively(self):
        response = self.client.post(
            "/api/employees/",
            self.valid_payload(
                email="EXISTING.EMPLOYEE@EXAMPLE.COM"
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_negative_salary_is_rejected(self):
        response = self.client.post(
            "/api/employees/",
            self.valid_payload(salary="-100.00"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_phone_is_rejected(self):
        response = self.client.post(
            "/api/employees/",
            self.valid_payload(phone="invalid-phone"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_employee_name_is_rejected(self):
        response = self.client.post(
            "/api/employees/",
            self.valid_payload(name="   "),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_delete_deactivates_instead_of_removing(self):
        employee_id = self.employee.id

        response = self.client.delete(
            f"/api/employees/{employee_id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.employee.refresh_from_db()

        self.assertFalse(self.employee.is_active)
        self.assertTrue(
            Employee.objects.filter(pk=employee_id).exists()
        )

    def test_employee_history_relationship_is_preserved(self):
        employee_id = self.employee.id

        self.client.delete(f"/api/employees/{employee_id}/")

        self.assertTrue(
            Employee.objects.filter(pk=employee_id).exists()
        )

    def test_employee_role_cannot_access_employee_api(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.get("/api/employees/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
