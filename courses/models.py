import uuid
from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=50,unique=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

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

    difficulty = models.CharField(
            max_length=20,
            choices=Difficulty.choices,
            default=Difficulty.BEGINNER,
            )
    tags = models.ManyToManyField(
            Tag,
            blank=True,
            related_name="courses"
            )
    language = models.CharField(
            max_length=50,
            default="English",
            )
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(
            max_digits=8,
            decimal_places=2,
            null=True,
            blank=True,
            help_text="Leave blank if the course is free",
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
    is_paid = models.BooleanField(default=False)

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
        on_delete=models.CASCADE,
        related_name="submissions"
        )
    file = models.FileField(upload_to="assignments/")
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(null=True,blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("assignment","student")
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    
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

class CourseOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="orders")
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.status}"
