from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseForbidden
from .forms import CourseForm
from .models import Course, Enrollment,Module,Lecture
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

@login_required
def course_detail(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    role = request.user.profile.role
    modules = course.modules.all()

    if role == "student":
        if not Enrollment.objects.filter(student=request.user,course=course).exists():
            return HttpResponseForbidden("You are not enrolled in this course.")
    elif role == "teacher":
        if course.teacher != request.user:
            return HttpResponseForbidden("You can only view your own courses.")
    else:
        #Maybe something for admin later
        pass
    #Basic info for enrollment count
    enrolled_students_count = course.enrollments.count()

    return render(request,"courses/course_detail.html",{
        "course":course,
        "role":role,
        "modules":modules,
        "enrolled_students_count":enrolled_students_count,
    })

@login_required
def lecture_detail(request,lecture_id):
    lecture = get_object_or_404(Lecture,id=lecture_id)
    course = lecture.module.course

    return render(request,"courses/lecture_detail.html",{
        "lecture":lecture,
        "course":course,
        })
@login_required
def add_module(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    if request.user != course.teacher:
        return HttpResponseForbidden()

    if request.method == "POST":
        title = request.POST.get("title")
        order = request.POST.get("order")

        Module.objects.create(
            course = course,
            title = title,
            order = order
        )

        return redirect("courses:course_detail",course.id)
    return render(request,"courses/add_module.html",{"course":course})

@login_required
def add_lecture(request,module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.user != course.teacher:
          return HttpResponseForbidden("You are not the teacher of this course.")

    if request.method == "POST":
        Lecture.objects.create(
            module=module,
            title=request.POST.get("title"),
            notes=request.POST.get("notes"),
            video_url=request.POST.get("video_url"),
            order = request.POST.get("order")
        )

        return redirect("courses:course_detail",course.id)

    return render(request,"courses/add_lecture.html",{"module":module})

@login_required
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.user != course.teacher:
        return HttpResponseForbidden("You are not allowed to edit this module.")

    if request.method == "POST":
        module.title = request.POST.get("title")
        module.order = request.POST.get("order")
        module.save()

        return redirect("courses:course_detail",course.id)

    return render(request,"courses/edit_module.html",{"module":module})

@login_required
def delete_module(request,module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.user != course.teacher:
        return HttpResponseForbidden("You are not the teacher of this course.")

    if request.method == "POST":
        module.delete()
        return redirect("courses:course_detail",course.id)

    return render(request,"courses/delete_module.html",{"module":module})

