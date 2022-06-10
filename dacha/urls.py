from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions, authentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.i18n import i18n_patterns

from .views import HomeApiView


schema_view = get_schema_view(
    openapi.Info(
        title="DachaTurizm API",
        default_version="v1",
        description="API",
        license=openapi.License(name="BSD License"),
    ),
    permission_classes=(permissions.IsAuthenticated,),
    authentication_classes=(authentication.SessionAuthentication,)
)

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
)


urlpatterns += [
    path("i18n/", include("django.conf.urls.i18n")),
    path("rosetta/", include("rosetta.urls")),
    path("api/", include("api.urls")),
    path(
        "swagger/",
        schema_view.with_ui(
            "swagger",
            cache_timeout=0
        ),
        name="schema-swagger-ui"
    ),
    path("summernote/", include("django_summernote.urls")),
    path("", HomeApiView.as_view()),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
