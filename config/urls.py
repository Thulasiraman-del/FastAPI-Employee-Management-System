from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("api/", include("attendance.urls")),
    path("api/", include("employees.urls")),
    path("api/auth/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("departments.urls")),
]

urlpatterns += [path('api/', include('leave_management.urls'))]

urlpatterns += [path('api/reports/', include('reports.urls'))]


urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
