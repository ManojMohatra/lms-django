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
    profile = request.user.profile
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")

    course_data = []

    for enrollment in enrollments:
        course = enrollment.course

        total_lectures = Lecture.objects.filter(module__course=course).count()

        completed_lectures = LectureProgress.objects.filter(
            student=request.user,
            lecture__module__course=course,
            completed=True
            ).count()
        progress_percent = 0
        
        if total_lectures > 0:
            progress_percent = int((completed_lectures / total_lectures) * 100)

        #First find incomplete lecture (Resume logic)
        next_lecture = Lecture.objects.filter(
            module__course=course
               ).exclude(
                   lectureprogress__student=request.user,
                   lectureprogress__completed=True
               ).order_by('module__order', 'order').first()

        course_data.append({
            "course":course,
            "progress_percent":progress_percent,
            "next_lecture":next_lecture
            })

    return render(request,"accounts/dashboard.html",{
        "profile":profile,
        "course_data":course_data
    })



