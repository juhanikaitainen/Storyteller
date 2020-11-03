from django.urls import path
from .views import *

app_name = 'helpp'

urlpatterns = [
    path('', home, name='home'),
]