from django.shortcuts import render
from courses.models import Course
from courses.recommendation import recommend_for_user

def home(request):
    courses = Course.objects.all()[:3]

    recommended_course = None
    if request.user.is_authenticated:
        recommended_courses = recommend_for_user(request.user)
        
        return render(request,"core/home.html",{
            "courses": courses,
            "recommended_courses":recommended_courses
             })
    return render(request,"core/home.html",{
        "courses":courses
    })
