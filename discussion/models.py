from django.db import models
from django.contrib.auth.models import User
from courses.models import Course

class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    parent = models.ForeignKey(
        "self",
         null =True,
         blank =True,
         on_delete=models.CASCADE,
         related_name="replies"
         )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def _str_(self):
        return f"{self.user.username} - {self.content[:30]}"
    
