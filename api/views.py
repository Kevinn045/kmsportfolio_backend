import os

from django.core.mail import send_mail
from google import genai

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Blog, Project, Visitor
from .serializers import BlogSerializer, ProjectSerializer

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(
        {
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
        }
    )


@api_view(["POST"])
def ai_chat(request):
    user_message = request.data.get("message")

    if not user_message:
        return Response(
            {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
You are Kevin Muse's portfolio assistant.

Your job is to answer questions about Kevin Muse,
his portfolio, projects, skills, education, and experience.

If the question is unrelated to Kevin Muse or his portfolio,
politely explain that you can only answer questions about Kevin
and his professional portfolio.

User question:
{user_message}
""",
        )

        return Response({"reply": response.text})

    except Exception as e:
        print("AI CHAT ERROR:", repr(e))

        return Response(
            {"error": "AI assistant is temporarily unavailable."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def contact(request):
    name = request.data.get("name")
    email = request.data.get("email")
    message = request.data.get("message")

    if not all([name, email, message]):
        return Response(
            {"error": "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    send_mail(
        f"Message from {name}",
        message,
        email,
        ["kevinmuse45@gmail.com"],
    )

    return Response({"success": True})


@api_view(["GET"])
def get_blog(request):
    blogs = Blog.objects.all().order_by("-created")
    return Response(BlogSerializer(blogs, many=True).data)


@api_view(["GET"])
def track_visit(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
    Visitor.objects.create(ip_address=ip)
    return Response({"status": "tracked"})
