from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.auth.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/voice/", include("apps.voice.urls")),
    path("api/background/", include("apps.background.urls")),
    path("api/interview/", include("apps.interview.urls")),
    path("api/deepfake/", include("apps.deepfake.urls")),
    path("api/scoring/", include("apps.scoring.urls")),
    path("api/proctoring/", include("apps.proctoring.urls")),
    path("api/coaching/", include("apps.coaching.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/orchestrator/", include("apps.orchestrator.urls")),
]
