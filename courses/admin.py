from django.contrib import admin
from .models  import Course, Enrollment,Module,Lecture,Tag

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Module)
admin.site.register(Lecture)
admin.site.register(Tag)



