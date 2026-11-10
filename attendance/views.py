from rest_framework.viewsets import ModelViewSet

from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.permissions import IsAdminOrHR


class AttendanceViewSet(ModelViewSet):

    queryset = Attendance.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    serializer_class = AttendanceSerializer

    permission_classes = [IsAdminOrHR]

    search_fields = [
        "employee__name",
        "employee__email",
        "employee__position",
        "notes",
    ]

    ordering_fields = [
        "attendance_date",
        "check_in",
        "check_out",
        "created_at",
    ]

    ordering = ["-attendance_date"]

    filterset_fields = [
        "employee",
        "attendance_date",
        "status",
    ]
