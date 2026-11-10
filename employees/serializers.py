from rest_framework import serializers

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "position",
            "salary",
            "department",
            "department_name",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Employee name cannot be empty."
            )
        return value

    def validate_email(self, value):
        value = value.strip().lower()

        queryset = Employee.objects.filter(email__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "An employee with this email already exists."
            )

        return value

    def validate_phone(self, value):
        return value.strip()

    def validate_position(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Position cannot be empty."
            )
        return value

    def validate_salary(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Salary cannot be negative."
            )
        return value
