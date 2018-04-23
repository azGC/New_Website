from django.conf.urls import *
from . import views
from django.conf.urls.static import static
from dashboard.views import carOwnerChartPage, carOwnerChart, my_login
urlpatterns = [
    # index
    url(r'^$', views.index, name='index'),
    # login
    url(r'^login', my_login, name='my_login'),
    # logout
    # url(r'^logout', my_logout, name='my_logout'),

    # car dashboard page
    url(r'^auto_page', carOwnerChartPage, name='carEchart'),
    url(r'^auto/$', carOwnerChart, name='carEchartPage'),

]


