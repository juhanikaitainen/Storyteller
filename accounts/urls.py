from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', accounts_home, name='home'),
    path('add/', coins_add, name='add'),
    path('withdraw/', coins_withdraw, name='withdraw'),
    path('history/', transaction_history, name='history'),
]