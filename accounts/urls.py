from django.urls import path
from .views import register, dashboard, UserLoginView, UserLogoutView

app_name = 'accounts'

urlpatterns = [
    path('register/',register,name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('logout/',UserLogoutView.as_view(),name='logout'),
    path('dashboard/',dashboard,name='dashboard'),
]
