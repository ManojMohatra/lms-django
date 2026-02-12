from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from courses.models import Course, Enrollment
from .models import Message


def course_chat(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # ---- Permission Check ----
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    is_teacher = course.teacher == request.user

    if not (is_enrolled or is_teacher):
        return HttpResponseForbidden(
            "You do not have access to this course discussion."
        )

    # ---- Handle Message Submission ----
    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        if content:
            parent = None

            if parent_id:
                # Ensure parent message belongs to same course
                parent = Message.objects.filter(
                    id=parent_id,
                    course=course
                ).first()

            Message.objects.create(
                course=course,
                user=request.user,   
                content=content,
                parent=parent
            )

        return redirect("chat:course_chat", course_id=course.id)

    # ---- Fetch Top-Level Messages ----
    messages = Message.objects.filter(
        course=course,
        parent__isnull=True
    ).order_by("-created_at")

    return render(request, "chat/course_chat.html", {
        "course": course,
        "messages": messages
    })
