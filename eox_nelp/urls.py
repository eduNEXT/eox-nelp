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
from django.conf.urls import url, include
from django.contrib import admin

from eox_nelp import views
#from eox_nelp.api_schema import docs_ui_view

app_name = 'eox_nelp' # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^eox-info$', views.info_view),
    url(r'^courses/', include('eox_nelp.course_api.urls')),
   # url(r'^api/', include('eox_nelp.api.urls', namespace='eox-api')),
    #url(r'^data-api/', include('eox_nelp.api.data.v1.urls', namespace='eox-data-api')),
    #url(r'^api-docs/$', docs_ui_view, name='apidocs-ui'),

]
