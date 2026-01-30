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

def enroll_course(request,course_id):
    if request.user.profile.role != "student":
        return HttpResponseForbidden("Only students can enroll.")

    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        student = request.user,
        course = course
    )
    #This is to make sure that they are redirected to the page that they were previously on instead of just a single hardcoded page
    next_page = request.GET.get("next") or "courses:course_list"
    return redirect(next_page)

def unenroll_course(request,course_id):
    if request.user.profile.role != "student":
        return HttpResponseForbidden("Only students can unenroll.")

    Enrollment.objects.filter(
        student=request.user,
        course_id=course_id
    ).delete()

    #This is to make sure that they are redirected to the page that they were previously on instead of just a single hardcoded page
    next_page = request.GET.get("next") or "courses:my_courses"

    return redirect(next_page)

@login_required
def my_courses(request):
    user = request.user
    role = user.profile.role

    if role == "student":
        courses = Course.objects.filter(enrollments__student=user)
    elif role == "teacher":
        courses = Course.objects.filter(teacher=user)
    else:
        courses = Course.objects.none()

    return render(request,"courses/my_courses.html",{
        "courses":courses,
        "role":role,
    })

@login_required
def edit_course(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    if request.user.profile.role != "teacher" or course.teacher != request.user:
        return HttpResponseForbidden("You cannot edit this course")

    if request.method == "POST":
        form = CourseForm(request.POST,instance=course)
        if form.is_valid():
            form.save()
            return redirect("courses:my_courses")
    else:
        form = CourseForm(instance=course)
    return render(request,"courses/edit_course.html",{"form":form,"course":course})

