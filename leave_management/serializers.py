from rest_framework import serializers
from employees.models import Employee
from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    employee_name = serializers.CharField(
        source="employee.name",
        read_only=True,
    )
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.username",
        read_only=True,
        allow_null=True,
    )
    leave_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "start_date",
            "end_date",
            "leave_days",
            "reason",
            "status",
            "applied_at",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "review_comments",
        ]
        read_only_fields = [
            "id",
            "status",
            "applied_at",
            "reviewed_by",
            "reviewed_at",
            "review_comments",
        ]

    def get_leave_days(self, obj) -> int:
        return (obj.end_date - obj.start_date).days + 1

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )
        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None),
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be earlier than start date."
            })

        reason = attrs.get("reason")
        if reason is not None:
            reason = reason.strip()
            if not reason:
                raise serializers.ValidationError({
                    "reason": "Reason cannot be empty."
                })
            attrs["reason"] = reason

        if self.instance and "employee" in attrs:
            if attrs["employee"].id != self.instance.employee_id:
                raise serializers.ValidationError({
                    "employee": "The employee cannot be changed."
                })

        return attrs
