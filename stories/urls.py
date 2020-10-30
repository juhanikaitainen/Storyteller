from django.urls import path
from .views import *

app_name = 'stories'

urlpatterns = [
    path('', story_home, name = 'home'),  # done
    path('all/', story_list, name = 'list'), # done
    path('my/', story_my, name = 'my'), # done
    path('new/', story_new, name='new'),
    path('new/valid/', story_valid, name='valid'),
    path('detail/<int:id>/', story_detail, name='detail'), # done
    path('buy/<int:id>/', story_buy, name='buy'), # done
    path('read/<int:storyid>/<int:sectionid>/', story_read, name='read'),
    path('approve/', story_approve, name='approve'), # done
    path('approve/<int:id>/', story_approve_id, name='approve-id'), # done
]