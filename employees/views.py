from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Employee
from .serializers import EmployeeSerializer
from accounts.permissions import IsAdminOrHR


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.select_related("department").all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrHR]

    search_fields = [
        "name",
        "email",
        "position",
        "department__name",
    ]

    ordering_fields = [
        "name",
        "salary",
        "created_at",
        "position",
    ]

    ordering = ["id"]

    filterset_fields = [
        "department",
        "is_active",
    ]

    def destroy(self, request, *args, **kwargs):
        employee = self.get_object()

        if not employee.is_active:
            return Response(
                {"detail": "Employee is already inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee.is_active = False
        employee.save(update_fields=["is_active", "updated_at"])

        return Response(
            {"detail": "Employee deactivated successfully."},
            status=status.HTTP_200_OK,
        )
