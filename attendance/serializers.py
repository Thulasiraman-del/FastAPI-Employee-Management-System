from rest_framework import serializers

from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee.name",
        read_only=True,
    )

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "attendance_date",
            "check_in",
            "check_out",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        check_in = attrs.get(
            "check_in",
            getattr(self.instance, "check_in", None),
        )
        check_out = attrs.get(
            "check_out",
            getattr(self.instance, "check_out", None),
        )

        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({
                "check_out": "Check-out must be later than check-in."
            })

        return attrs

    def validate_notes(self, value):
        return value.strip()
