from django.core.exceptions import PermissionDenied
from .models import Customuser

def writer_required(function):
    def wrap(request, *args, **kwargs):
        builtin_user = request.user
        custom_user = Customuser.objects.get(djangouser=builtin_user)
        if custom_user.usertype >= Customuser.Category.WRITER:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def moderator_required(function):
    def wrap(request, *args, **kwargs):
        builtin_user = request.user
        custom_user = Customuser.objects.get(djangouser=builtin_user)
        if custom_user.usertype >= Customuser.Category.MODERATOR:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def not_moderator_required(function):
    def wrap(request, *args, **kwargs):
        builtin_user = request.user
        custom_user = Customuser.objects.get(djangouser=builtin_user)
        if custom_user.usertype < Customuser.Category.MODERATOR:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def not_frozen(function):
    def wrap(request, *args, **kwargs):
        builtin_user = request.user
        custom_user = Customuser.objects.get(djangouser=builtin_user)
        if custom_user.frozen:
            raise PermissionDenied
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

