from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

# Language switch endpoint (IMPORTANT)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('materials/', include('materials.urls')),
    path("discussion/", include("discussion.urls")),
    path('quiz/', include('quiz.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
)

# Media 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
