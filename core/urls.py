from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path('about/', TemplateView.as_view(template_name="core/about.html"), name='about'),
    path('contact/', TemplateView.as_view(template_name="core/contact.html"), name='contact'),
]
