from django.shortcuts import render
from courses.models import Course

def home(request):
    courses = Course.objects.all()[:3]
    return render(request,"core/home.html",{
        "courses": courses
        })

