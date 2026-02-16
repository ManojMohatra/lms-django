from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Material
from django.contrib import messages
from courses.models import Lecture, Enrollment,Course

@login_required
def lecture_materials(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.module.course
    is_teacher = (course.teacher == request.user)
    
    # Permission check
    is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()
    if not (is_teacher or is_enrolled):
        raise PermissionDenied("Access denied.")

    if request.method == "POST" and is_teacher:
        title = request.POST.get('title')
        link = request.POST.get('link') # Generic link
        if title and link:
            Material.objects.create(lecture=lecture, title=title, link=link)
            messages.success(request, 'Material added successfully!')
    
    # Always redirect back to the lecture detail page
    return redirect('courses:lecture_detail', lecture_id=lecture.id)

@login_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    lecture_id = material.lecture.id
    
    if material.lecture.module.course.teacher == request.user:
        material.delete()
        messages.success(request, 'Material deleted.')
    
    return redirect('courses:lecture_detail', lecture_id=lecture_id)
