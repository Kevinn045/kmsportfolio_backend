import os

from django.core.mail import send_mail
from openai import OpenAI

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status

from .models import Blog, Project, Visitor
from .serializers import BlogSerializer, ProjectSerializer

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email,
        "is_staff": request.user.is_staff,
    })
@api_view(['POST'])
def ai_chat(request):
    user_message = request.data.get("message")
    history = request.data.get("history", [])
    projects = Project.objects.all()
    blogs = Blog.objects.all()
    project_list = "\n".join(
        [f"- {p.title}: {p.description}" for p in projects])
    blog_list = "\n".join([f"- {b.title}" for b in blogs])
    messages = [
        {
            "role": "system",
            "content": f"""
            You are an AI assistant for a developer portfolio.

            Developer Info:
            - Name: kevin muse
            - Skills: Django, React, Python, AI
            - Projects: Portfolio, API systems, dashboards

            Projects:
            {project_list}

            Blog Posts:
            {blog_list}

            Answer professionally and concisely.
            """
        }
    ]
    for msg in history:
        messages.append(msg)

    # add current message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages  # type: ignore
    )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    reply = response.choices[0].message.content
    return Response({"reply": reply})


@api_view(['GET'])
def get_projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
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
        ['kevinmuse45@gmail.com'],
    )

    return Response({"success": True})


@api_view(['GET'])
def get_blog(request):
    blogs = Blog.objects.all().order_by('-created')
    return Response(BlogSerializer(blogs, many=True).data)


@api_view(['GET'])
def track_visit(request):
    ip = request.META.get(
        "HTTP_X_FORWARDED_FOR",
        request.META.get("REMOTE_ADDR")
    )
    Visitor.objects.create(ip_address=ip)
    return Response({"status": "tracked"})
