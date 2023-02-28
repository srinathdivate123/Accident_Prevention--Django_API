from django.urls import path
from . import views
urlpatterns = [
    path('get', views.RepeatGetInfoView, name='RepeatGetInfoView'),
    path('test', views.testGetView, name='testGetView'),
]