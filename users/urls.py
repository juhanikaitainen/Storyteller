from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('signup/', signup_view, name='signup-view'),
    path('login/', login_view, name='login-view'),
    path('logout/', logout_view, name='logout-view'),
    path('settings/', settings_view, name='settings-view'),
    path('settings/freeze/', freeze_view, name='freeze-view'),
    path('settings/freeze/<int:id>/', freeze_id, name='freeze-id'),
    path('settings/unfreeze/', unfreeze_view, name='unfreeze-view'),
    path('settings/unfreeze/<int:id>', unfreeze_id, name='unfreeze-id'),
    path('settings/privilege-application/', privilege_application, name='privilege-application'),
    path('settings/grant-privileges/', grant_privilege, name='grant-privilege'),
    path('settings/grant-privileges/grant/<int:id>/', grant_privilege_id, name='grant-id'),
    path('settings/grant-privileges/reject/<int:id>/', reject_privilege_id, name='reject-id'),
    path('settings/privilege-application/already-applied/', already_applied, name='already-applied'),
]