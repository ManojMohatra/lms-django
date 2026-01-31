from django.contrib import admin
from .models  import Course, Enrollment,Module,Lecture

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Module)
admin.site.register(Lecture)



