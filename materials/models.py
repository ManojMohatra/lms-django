from django.db import models
from courses.models import Lecture

class Material(models.Model):
    lecture = models.ForeignKey(
        Lecture, 
        on_delete=models.CASCADE, 
        related_name="materials"
    )
    title = models.CharField(max_length=255)
    drive_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.lecture.title}"