from django.core.mail import send_mail
from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Blog, Project, Visitor
from .serializers import BlogSerializer, ProjectSerializer
from django.core.mail import send_mail


from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@api_view(['POST'])
def ai_chat(request):
    user_message = request.data.get("message")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            You are an AI assistant for a developer portfolio.

            Developer Info:
            - Name: Your Name
            - Skills: Django, React, Python, AI
            - Projects: Portfolio, API systems, dashboards

            Answer professionally and concisely.
            """},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    return Response({"reply": reply})


@api_view(['GET'])
def get_projects(request):
    return Response(ProjectSerializer(Project.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['POST'])
def contact(request):
    name = request.data['name']
    email = request.data['email']
    message = request.data['message']

    send_mail(
        f"Message from {name}",
        message,
        email,
        ['your@email.com'],
    )

    return Response({"success": True})


@api_view(['GET'])
def get_blog(request):
    blogs = Blog.objects.all().order_by('-created')
    return Response(BlogSerializer(blogs, many=True).data)


@api_view(['GET'])
def track_visit(request):
    ip = request.META.get('REMOTE_ADDR')
    Visitor.objects.create(ip_address=ip)
    return Response({"status": "tracked"})
