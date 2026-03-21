from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses_taught"
    )

    thumbnail = models.ImageField(
        upload_to ="course_thumbnails/",
        null=True,
        blank=True
        )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course=models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student','course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Module(models.Model):
    course = models.ForeignKey(
        "Course",
         on_delete=models.CASCADE,
         related_name="modules"
    )

    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Lecture(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

        
    def __str__(self):
        return f"{self.title} ({self.module.title})"


class LectureProgress(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    lecture = models.ForeignKey("Lecture",on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True,blank=True)

    class Meta:
        unique_together = ("student","lecture")

    def __str__(self):
        return f"{self.student.username} - {self.lecture.title}"

class Assignment(models.Model):
    lecture = models.ForeignKey(
        "Lecture",
        on_delete=models.CASCADE,
        related_name ="assignments"
        )
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField(null=True,blank=True)
    max_points = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
        )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
        )
    file = models.FileField(upload_to="assignments/")
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(null=True,blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("assignment","student")
    def __str__(self):
        return f"{self.student.username} - {self.assigment.title}"

    
class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(User, on_delete=models.CASCADE)  
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')  # one review per student

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"