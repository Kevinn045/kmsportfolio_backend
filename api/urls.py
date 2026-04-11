from django.urls import path
from .views import add_project, contact, get_projects
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('projects/', get_projects),
    path('add-project/', add_project),
    path('login/', TokenObtainPairView.as_view()),
    path('contact/', contact),

]
