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
    is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()
    if not (is_teacher or is_enrolled):
        raise PermissionDenied("You are not enrolled in this course.")
    if request.method == "POST" and is_teacher:
        title = request.POST.get('title')
        link = request.POST.get('drive_link')
        if title and link:
            Material.objects.create(lecture=lecture, title=title, drive_link=link)
            messages.success(request, 'Material uploaded successfully!')
            
            # Check if request came from all_materials page
            referer = request.META.get('HTTP_REFERER', '')
            if 'all' in referer:
                return redirect('all_materials')
            
            
            return redirect('courses:lecture_detail', lecture_id=lecture.id)

    materials = lecture.materials.all()
    return render(request, 'materials/lecture_materials.html', {
        'lecture': lecture,
        'materials': materials,
        'is_teacher': is_teacher
    })


@login_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    lecture = material.lecture
    course = lecture.module.course
    
    # Only the teacher can delete materials
    if course.teacher != request.user:
        raise PermissionDenied("Only the course teacher can delete materials.")
    
    if request.method == "POST":
        material.delete()
        messages.success(request, 'Material deleted successfully!')

        referer = request.META.get('HTTP_REFERER', '')
        if 'all' in referer:
            return redirect('all_materials')
        return redirect('courses:lecture_detail', lecture_id=lecture.id)
    
    return redirect('courses:lecture_detail', lecture_id=lecture.id)


@login_required
def all_materials(request):

    enrolled_courses = Enrollment.objects.filter(student=request.user).select_related('course')
    teaching_courses = Course.objects.filter(teacher=request.user)
    all_courses = list(teaching_courses) + [enrollment.course for enrollment in enrolled_courses]
    all_courses = list(set(all_courses))
    
    courses_with_materials = []   
    for course in all_courses:
        materials_data = []
        
        for module in course.modules.all().order_by('order'):
            for lecture in module.lectures.all().order_by('order'):
                materials = Material.objects.filter(lecture=lecture)
                if materials.exists():
                    materials_data.append({
                        'module': module,
                        'lecture': lecture,
                        'materials': materials
                    })
        
        if materials_data:  # Only include courses that have materials
            courses_with_materials.append({
                'course': course,
                'materials_data': materials_data,
                'is_teacher': course.teacher == request.user
            })
    
    return render(request, 'materials/all_materials.html', {
        'courses_with_materials': courses_with_materials
    })
