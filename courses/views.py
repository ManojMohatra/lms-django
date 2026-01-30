from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .forms import CourseForm
from .models import Course

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
    return render(request,"courses/course_list.html",{"courses": courses})


