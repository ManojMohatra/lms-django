from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseForbidden
from .forms import CourseForm,AssignmentForm
from .models import Course, Enrollment,Module,Lecture,LectureProgress,Assignment,Submission
from django.contrib.auth.decorators import login_required
from discussion.models import Comment
from django.utils import timezone

def create_course(request):
    if request.user.profile.role != "teacher":
        return HttpResponseForbidden("Only teacher can create courses.")

    if request.method == "POST":
        form = CourseForm(request.POST,request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("accounts:dashboard")
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

@login_required
def unenroll_course(request, course_id):
    # 1. Security check: Only students allowed
    if request.user.profile.role != "student":
        return HttpResponseForbidden("Only students can unenroll.")

    # 2. Get the specific enrollment or 404
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course_id=course_id
    )

    if request.method == "POST":
        # 3. Perform the deletion
        enrollment.delete()
        # 4. Redirect specifically to the course list
        return redirect("courses:course_list")

    # 5. If GET, show the confirmation page
    return render(request, "courses/confirm_unenroll.html", {
        "course": enrollment.course,
        "next": "courses:course_list"  # Provides a safe return path for the 'Cancel' link
    })


@login_required
def edit_course(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    if request.user.profile.role != "teacher" or course.teacher != request.user:
        return HttpResponseForbidden("You cannot edit this course")

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES ,instance=course)
        if form.is_valid():
            form.save()
            return redirect("courses:course_detail",course_id=course.id)
    else:
        form = CourseForm(instance=course)
    return render(request,"courses/edit_course.html",{"form":form,"course":course})

@login_required
def course_detail(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    role = request.user.profile.role
    modules = course.modules.all()
    comment_count = Comment.objects.filter(course=course).count()

    total_lectures = Lecture.objects.filter(module__course=course).count()

    completed_lectures = LectureProgress.objects.filter(
        student=request.user,
        lecture__module__course=course,
        completed=True
        ).count()
    progress_percent = 0
    if total_lectures > 0:
        progress_percent = int((completed_lectures / total_lectures) * 100)
        
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
        "comment_count":comment_count,
        "progress_percent": progress_percent
    })


@login_required
def lecture_detail(request, lecture_id):
    # Added 'quizzes' and 'assignments' to prefetch_related for efficiency
    # This ensures that lecture.quizzes.all() in the template doesn't trigger new queries
    lecture = get_object_or_404(
        Lecture.objects.prefetch_related('materials', 'quizzes', 'assignments'), 
        id=lecture_id
    )
    
    course = lecture.module.course
    is_teacher = (course.teacher == request.user)
    assignments = lecture.assignments.all()
    
    # Process POST actions
    if request.method == "POST":
        # 1. Handle Student Assignment Upload
        if 'file' in request.FILES:
            assignment_id = request.POST.get('assignment_id')
            target_assignment = get_object_or_404(Assignment, id=assignment_id)
            
            submission, created = Submission.objects.get_or_create(
                assignment=target_assignment, 
                student=request.user
            )
            submission.file = request.FILES['file']
            submission.save()
            return redirect('courses:lecture_detail', lecture_id=lecture.id)

        # 2. Handle Lesson Completion Toggle
        elif 'action' in request.POST:
            progress, created = LectureProgress.objects.get_or_create(
                student=request.user, 
                lecture=lecture
            )
            progress.completed = (request.POST.get('action') == 'mark')
            if progress.completed:
                progress.completed_at = timezone.now()
            progress.save()
            return redirect('courses:lecture_detail', lecture_id=lecture.id)

    # Prepare Data for Template
    completed = False
    if not is_teacher:
        # Check progress
        completed = LectureProgress.objects.filter(
            student=request.user, 
            lecture=lecture, 
            completed=True
        ).exists()

        # Attach user submissions to assignments
        user_subs = {
            s.assignment_id: s for s in Submission.objects.filter(
                assignment__in=assignments, 
                student=request.user
            )
        }
        for assignment in assignments:
            assignment.user_submission = user_subs.get(assignment.id)

    return render(request, "courses/lecture_detail.html", {
        "lecture": lecture,
        "course": course,
        "is_teacher": is_teacher,
        "assignments": assignments,
        "completed": completed,
        # 'quizzes' are available via 'lecture.quizzes.all' due to the prefetch
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



@login_required
def edit_lecture(request,lecture_id):
    lecture = get_object_or_404(Lecture,id=lecture_id)
    course = lecture.module.course

    if request.user != course.teacher:
        return HttpResponseForbidden() #Maybe can add some message later

    if request.method == "POST":
        lecture.title = request.POST.get("title")
        lecture.notes = request.POST.get("notes")
        lecture.video_url = request.POST.get("video_url")
        lecture.order = request.POST.get("order")

        lecture.save()

        return redirect("courses:course_detail",course.id)

    return render(request,"courses/edit_lecture.html",{"lecture":lecture})

@login_required
def delete_lecture(request,lecture_id):
    lecture = get_object_or_404(Lecture,id=lecture_id)
    course = lecture.module.course

    if request.user != course.teacher:
        return HttpResponseForbidden()  #Maybe some message later

    if request.method == "POST":
        lecture.delete()
        return redirect("courses:course_detail", course.id)

    return render(request, "courses/delete_lecture.html", {"lecture": lecture})

@login_required
def delete_course(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    if request.user != course.teacher and not request.user_is_staff:
        return HttpResponseForbidden()

    if request.method == "POST":
        course.delete()
        return redirect("accounts:dashboard")

    return render(request,"courses/delete_course.html",{
        "course":course
        })

@login_required
def create_assignment(request, lecture_id):
    lecture = get_object_or_404(Lecture,id=lecture_id)

    if request.user != lecture.module.course.teacher:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.lecture = lecture
            assignment.save()
            return redirect("courses:lecture_detail",lecture_id=lecture.id)
    else:
        form = AssignmentForm()

    return render(request,'courses/assignment_form.html',{
        'form':form,
        'lecture':lecture
        })
            
