from django.shortcuts import render
from courses.models import Course
from courses.recommendation import recommend_for_user
from django.db.models import Avg
from django.db.models.functions import Round
def home(request):
    courses = Course.objects.annotate(avg_rating=Avg('reviews__rating'),
     rounded_rating=Round(Avg('reviews__rating')))[:3]
    recommended_course = None
    if request.user.is_authenticated:
        recommended_courses = recommend_for_user(request.user).annotate(
        avg_rating=Avg('reviews__rating'), rounded_rating=Round(Avg('reviews__rating')))
        
        return render(request,"core/home.html",{
            "courses": courses,
            "recommended_courses":recommended_courses
             })
    return render(request,"core/home.html",{
        "courses":courses
    })
