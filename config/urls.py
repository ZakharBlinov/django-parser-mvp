from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/vacancies/', permanent=False)),
    path('api/', include('parser_app.urls')),
    path('vacancies/', include('parser_app.urls')),
]