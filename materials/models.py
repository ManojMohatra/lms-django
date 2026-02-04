from django.db import models
from django.contrib.auth.models import User
from courses.models import Course

class Material(models.Model):
    MATERIAL_TYPES = (
        ("pdf", "PDF / Document"),
        ("video", "Video"),
        ("link", "External Link"),
        ("text", "Text Content"),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials"
    )

    title = models.CharField(max_length=255)
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPES
    )

    file = models.FileField(
        upload_to="materials/files/",
        blank=True,
        null=True
    )

    video_url = models.URLField(blank=True)
    external_link = models.URLField(blank=True)
    text_content = models.TextField(blank=True)

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"
