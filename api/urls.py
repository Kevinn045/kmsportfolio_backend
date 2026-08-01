from django.urls import path
from .views import (
    add_project,
    ai_chat,
    contact,
    get_blog,
    get_blog_post,
    get_projects,
    track_visit,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import profile

urlpatterns = [
    path("projects/", get_projects),
    path("add-project/", add_project),
    path("login/", TokenObtainPairView.as_view()),
    path("contact/", contact),
    path("chat/", ai_chat),
    path("blog/", get_blog),
    path("blog/<int:pk>/", get_blog_post),
    path("track/", track_visit),
    path("refresh/", TokenRefreshView.as_view()),
    path("profile/", profile),
]
