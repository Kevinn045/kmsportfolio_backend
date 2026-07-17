from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    link = models.URLField()
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    technologies = models.CharField(max_length=255)
    github = models.URLField(blank=True)
    live_demo = models.URLField(blank=True)
    class Meta:
       ordering = ['-id']
    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="blogs/", blank=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
       return self.title
class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    browser = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=100, blank=True)
    page = models.CharField(max_length=200, blank=True)
    def __str__(self):
       return self.ip_address
