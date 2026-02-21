from django.shortcuts import render,redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from courses.models import Course,Enrollment,Lecture,LectureProgress

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            user.profile.role = form.cleaned_data['role']
            user.profile.save()

            login(request,user)
            return redirect('accounts:dashboard')

    else:
        form = UserRegistrationForm()
    return render(request,'accounts/register.html',{'form':form})



class UserLoginView(LoginView):
    template_name = 'accounts/login.html'

class UserLogoutView(LogoutView):
    next_page = 'accounts:login'

@login_required
def dashboard(request):
    user = request.user
    role = user.profile.role
    context = {"role": role}

    # -------------------------
    # STUDENT DASHBOARD
    # -------------------------
    if role == "student":
        enrollments = Enrollment.objects.filter(student=user).select_related("course")
        course_data = []

        for enrollment in enrollments:
            course = enrollment.course

            # Total lectures in course
            total_lectures = Lecture.objects.filter(
                module__course=course
            ).count()

            # Completed lecture IDs
            completed_lecture_ids = LectureProgress.objects.filter(
                student=user,
                lecture__module__course=course,
                completed=True
            ).values_list("lecture_id", flat=True)

            completed_count = len(completed_lecture_ids)

            # Progress percentage
            progress_percent = 0
            if total_lectures > 0:
                progress_percent = int((completed_count / total_lectures) * 100)

            # Find next incomplete lecture
            next_lecture = Lecture.objects.filter(
                module__course=course
            ).exclude(
                id__in=completed_lecture_ids
            ).order_by("module__order", "order").first()

            course_data.append({
                "course": course,
                "progress_percent": progress_percent,
                "next_lecture": next_lecture
            })

        context["course_data"] = course_data

    # -------------------------
    # TEACHER DASHBOARD
    # -------------------------
    elif role == "teacher":
        teacher_courses = Course.objects.filter(teacher=user)
        context["teacher_courses"] = teacher_courses

    return render(request, "accounts/dashboard.html", context)
