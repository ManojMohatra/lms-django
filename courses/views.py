from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseForbidden
from .forms import CourseForm
from .models import Course, Enrollment
from django.contrib.auth.decorators import login_required

def create_course(request):
    if request.user.profile.role != "teacher":
        return HttpResponseForbidden("Only teacher can create courses.")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("courses:course_list")
    else:
        form = CourseForm()

    return render(request,"courses/create_course.html",{"form":form})




def course_list(request):
    courses = Course.objects.all()
    enrolled_courses = []

    if request.user.profile.role == "student":
        enrolled_courses = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id",flat=True)
        
    return render(request,
                  "courses/course_list.html",
                  {
                      "courses": courses,
                      "enrolled_courses":enrolled_courses
                  })

@login_required
def enroll_course(request,course_id):
    if request.user.profile.role != "student":
        return HttpResponseForbidden("Only students can enroll.")

    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        student = request.user,
        course = course
    )

    return redirect("courses:course_list")


@login_required
def unenroll_course(request,course_id):
    if request.user.profile.role != "student":
        return HttpResponseForbidden("Only students can unenroll.")

    Enrollment.objects.filter(
        student=request.user,
        course_id=course_id
    ).delete()

    return redirect("courses:course_list")
