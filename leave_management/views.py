from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdminOrHR
from employees.models import Employee
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer


class LeaveRequestViewSet(ModelViewSet):
    queryset = LeaveRequest.objects.none()
    serializer_class = LeaveRequestSerializer

    def get_permissions(self):
        if self.action in ["approve", "reject"]:
            return [IsAdminOrHR()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return LeaveRequest.objects.none()

        queryset = LeaveRequest.objects.select_related(
            "employee",
            "reviewed_by",
            "employee__department",
        )

        user = self.request.user
        is_admin_or_hr = (
            user.is_superuser
            or getattr(user, "role", None) in ("ADMIN", "HR")
        )

        if is_admin_or_hr:
            return queryset

        return queryset.filter(employee__email__iexact=user.email)

    def perform_create(self, serializer):
        user = self.request.user
        is_admin_or_hr = (
            user.is_superuser
            or getattr(user, "role", None) in ("ADMIN", "HR")
        )

        if is_admin_or_hr:
            if "employee" not in serializer.validated_data:
                raise ValidationError(
                    {"employee": "Select an employee for this leave request."}
                )
            serializer.save()
            return

        try:
            employee = Employee.objects.get(email__iexact=user.email)
        except Employee.DoesNotExist:
            raise ValidationError(
                "No employee profile is linked to your account email."
            )

        serializer.save(employee=employee)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        is_admin_or_hr = (
            user.is_superuser
            or getattr(user, "role", None) in ("ADMIN", "HR")
        )

        if not is_admin_or_hr and instance.status != LeaveRequest.Status.PENDING:
            raise PermissionDenied(
                "Only pending leave requests can be edited."
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        is_admin_or_hr = (
            user.is_superuser
            or getattr(user, "role", None) in ("ADMIN", "HR")
        )

        if not is_admin_or_hr and instance.status != LeaveRequest.Status.PENDING:
            raise PermissionDenied(
                "Only pending leave requests can be deleted."
            )

        instance.delete()

    def _review_leave_request(self, request, pk, new_status):
        if not hasattr(request.data, "get"):
            raise ValidationError({
                "review_comments": "Request body must contain valid review data."
            })

        comments = request.data.get("review_comments", "")

        if not isinstance(comments, str):
            raise ValidationError({
                "review_comments": "Review comments must be text."
            })

        comments = comments.strip()

        if len(comments) > 2000:
            raise ValidationError({
                "review_comments": "Review comments cannot exceed 2000 characters."
            })

        leave = self.get_object()

        # Re-fetch the latest database state while holding a row lock.
        leave = LeaveRequest.objects.select_for_update().get(pk=leave.pk)

        if leave.status != LeaveRequest.Status.PENDING:
            return Response(
                {"detail": "Only pending requests can be reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = new_status
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.review_comments = comments

        leave.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "review_comments",
            ]
        )

        return Response(self.get_serializer(leave).data)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._review_leave_request(
            request,
            pk,
            LeaveRequest.Status.APPROVED,
        )

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._review_leave_request(
            request,
            pk,
            LeaveRequest.Status.REJECTED,
        )
