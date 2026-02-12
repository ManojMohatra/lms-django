from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponseForbidden
from courses.models import Course, Enrollment
from .models import Message

def course_chat(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    if not Enrollment.objects.filter(
            student=request.user,
            course=course
            ).exists():
        return HttpResponseForbidden("You must be enrolled to access course discussion")


    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        if content:
            parent= None
            if parent_id:
                parent = Messages.objects.filter(id=parent_id).first()

            Message.objects.create(
                course=course,
                user=request.user,
                content=content,
                parent=parent
            )

        return redirect("chat:course_chat",course_id=course.id)

    messages = Message.objects.filter(
        course=course,
        parent__isnull=True
        ).order_by("-created_at")

    return render(request,"chat/course_chat.html",{
        "course":course,
        "messages":messages
    })


