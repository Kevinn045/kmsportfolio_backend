from django.urls import path
from .views import add_project, ai_chat, contact, get_blog, get_projects, track_visit
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('projects/', get_projects),
    path('add-project/', add_project),
    path('login/', TokenObtainPairView.as_view()),
    path('contact/', contact),
    path('chat/', ai_chat),
    path('blog/', get_blog),
    path('track/', track_visit)
]
