from rest_framework.permissions import BasePermission


class IsAdminOrHR(BasePermission):
    """
    Restrict administrative resources to Admin, HR and superusers.
    Employees and managers must use their dedicated self-service APIs.
    """

    message = "Only Admin and HR users can access this resource."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser
            or getattr(user, "role", None) in ("ADMIN", "HR")
        )
