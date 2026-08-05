import os

from django.core.mail import send_mail
from google import genai

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Blog, Project, Visitor, Contact
from .serializers import BlogSerializer, ProjectSerializer, ContactSerializer

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
        # Get portfolio projects
        projects = Project.objects.all()

        project_context = "\n".join([f"""
Project: {project.title}
Description: {project.description}
Technologies: {project.technologies}
GitHub: {project.github}
Live Demo: {project.live_demo}
""" for project in projects])

        # Get portfolio blog posts
        blogs = Blog.objects.all()

        blog_context = "\n".join([f"""
Blog Title: {blog.title}
Content: {blog.content}
""" for blog in blogs])

        # Give Gemini the actual portfolio information
        portfolio_context = f"""
PROJECTS
========
{project_context if project_context else "No projects available."}

BLOG POSTS
==========
{blog_context if blog_context else "No blog posts available."}
"""

        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"""
You are Kevin Muse's AI Portfolio Assistant.

Your job is to answer questions about Kevin Muse,
his portfolio, projects, blog posts, skills, education,
and professional experience.

IMPORTANT RULES:

1. Use the portfolio information provided below as your
   primary source of truth.

2. Do NOT invent projects, technologies, experience,
   education, links, or other information about Kevin.

3. If the requested information isn't contained in the
   portfolio data, say that the information isn't currently
   available in Kevin's portfolio.

4. If someone asks something unrelated to Kevin Muse or
   his portfolio, politely redirect them back to Kevin's
   portfolio.

5. When mentioning a project, use the actual project name
   from the portfolio data.

PORTFOLIO DATA
==============

{portfolio_context}

USER QUESTION
=============

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

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method in ["PATCH", "PUT"]:
        serializer = ProjectSerializer(project, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        project.delete()

        return Response(
            {"message": "Project deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


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

    # Save message to database
    Contact.objects.create(
        name=name,
        email=email,
        message=message,
    )

    # Send email notification
    try:
        send_mail(
            f"Message from {name}",
            message,
            email,
            ["kevinmuse45@gmail.com"],
        )
    except Exception as e:
        print("Email error:", e)

    return Response(
        {"success": True},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_contacts(request, pk=None):

    # GET all messages
    if request.method == "GET" and pk is None:
        contacts = Contact.objects.all().order_by("-created")
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    # Get one message
    contact = get_object_or_404(Contact, pk=pk)

    # Mark as read/unread
    if request.method == "PATCH":
        serializer = ContactSerializer(contact, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete
    if request.method == "DELETE":
        contact.delete()

        return Response(
            {"message": "Message deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_messages(request):
    messages = Contact.objects.all().order_by("-created")
    serializer = ContactSerializer(messages, many=True)

    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_message_read(request, pk):
    message = get_object_or_404(Contact, pk=pk)

    is_read = request.data.get("is_read")

    if not isinstance(is_read, bool):
        return Response(
            {"error": "is_read must be true or false."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    message.is_read = is_read
    message.save()

    serializer = ContactSerializer(message)

    return Response(serializer.data)


@api_view(["GET"])
def get_blog(request):
    blogs = Blog.objects.all().order_by("-created")
    return Response(BlogSerializer(blogs, many=True).data)


@api_view(["GET"])
def get_blog_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    serializer = BlogSerializer(post)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_blog(request):
    serializer = BlogSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_blog(request, pk):
    post = get_object_or_404(Blog, pk=pk)

    # UPDATE
    if request.method in ["PUT", "PATCH"]:
        serializer = BlogSerializer(
            post, data=request.data, partial=request.method == "PATCH"
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    if request.method == "DELETE":
        post.delete()

        return Response(
            {"message": "Blog post deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
def track_visit(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
    Visitor.objects.create(ip_address=ip)
    return Response({"status": "tracked"})
