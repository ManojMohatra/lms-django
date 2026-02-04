from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Material
from courses.models import Course, Enrollment

@login_required
def material_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    role = request.user.profile.role

    if role == "student":
        if not Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists():
            return HttpResponseForbidden("You are not enrolled in this course.")

    elif role == "teacher":
        if course.teacher != request.user:
            return HttpResponseForbidden("You are not the teacher of this course.")

    materials = course.materials.all()

    return render(request, "materials/material_list.html", {
        "course": course,
        "materials": materials,
        "role": role,
    })


@login_required
def add_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.profile.role != "teacher" or course.teacher != request.user:
        return HttpResponseForbidden("Only course teacher can add materials.")

    if request.method == "POST":
        Material.objects.create(
            course=course,
            title=request.POST.get("title"),
            material_type=request.POST.get("material_type"),
            file=request.FILES.get("file"),
            video_url=request.POST.get("video_url"),
            external_link=request.POST.get("external_link"),
            text_content=request.POST.get("text_content"),
            uploaded_by=request.user
        )
        return redirect("materials:material_list", course.id)

    return render(request, "materials/add_material.html", {"course": course})


