from rest_framework.viewsets import ModelViewSet

from .models import Department
from .serializers import DepartmentSerializer
from accounts.permissions import IsAdminOrHR


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrHR]

    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]
    filterset_fields = ["is_active"]
