"""eox_nelp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path

from eox_nelp import views

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path('eox-info/', views.info_view, name='eox-info'),
    path('courses/', include('eox_nelp.course_api.urls', namespace='nelp-course-api')),
    path('api/mfe_config/', include('eox_nelp.mfe_config_api.urls', namespace='mfe-config-api')),
    path('api/experience/', include('eox_nelp.course_experience.api.urls', namespace='course-experience-api')),
    path(
        'frontend/experience/',
        include('eox_nelp.course_experience.frontend.urls', namespace='course-experience-frontend'),
    ),
    path('api/stats/', include('eox_nelp.stats.api.urls', namespace='stats-api')),
    path('frontend/stats/', include('eox_nelp.stats.urls', namespace='stats-frontend')),
]
