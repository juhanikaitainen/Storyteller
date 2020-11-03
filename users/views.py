from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from .models import Customuser, Application
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CustomuserCreationForm, ApplicationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import not_moderator_required, writer_required, moderator_required, not_frozen

from accounts.models import Wallet
# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        customform = CustomuserCreationForm(request.POST)
        if(form.is_valid()):
            builtin_user = form.save()
            if(customform.is_valid()):
                customised_user = customform.save(commit=False)
                customised_user.djangouser = builtin_user
                customised_user.save()
                wallet = Wallet(balance=0.00, owner=builtin_user)
                wallet.save()
                login(request, builtin_user)
                return redirect('home-view')
            else:
                builtin_user.delete()
    else:
        form = UserCreationForm()
        customform = CustomuserCreationForm()
    return render(request, 'users/signup.html', { 'djangoform': form, 'customform': customform })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if(form.is_valid()):
            user = form.get_user()
            customuser = Customuser.objects.get(djangouser=user)  
            login(request, user)
            return redirect(f'{reverse("home-view")}?name={customuser.name}')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', { 'form': form })

@login_required(login_url='/users/login/')
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home-view')
    else:
        return HttpResponse("Illegal")

@login_required(login_url='/users/login/')
@not_frozen
def settings_view(request):
    userinfo = Customuser.objects.get(djangouser=request.user)
    is_mod = userinfo.usertype >= Customuser.Category.MODERATOR
    return render(request, 'users/settings.html', { 'is_mod': is_mod, 'userinfo': userinfo })

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def freeze_view(request):
    available_users = Customuser.objects.all().exclude(usertype=Customuser.Category.MODERATOR).filter(frozen=False)
    return render(request, 'users/freeze.html', { 'available_users': available_users })

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def unfreeze_view(request):
    banned_users = Customuser.objects.all().exclude(usertype=Customuser.Category.MODERATOR).filter(frozen=True)
    return render(request, 'users/unfreeze.html', { 'banned_users': banned_users })

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def freeze_id(request, id):
    query = Customuser.objects.filter(pk=id, frozen=False).exclude(usertype=Customuser.Category.MODERATOR)
    if len(query) > 0:
        query.update(frozen=True)
        return redirect('users:freeze-view')
    else:
        return HttpResponseBadRequest("This is not a valid request")

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def unfreeze_id(request, id):
    query = Customuser.objects.filter(pk=id, frozen=True).exclude(usertype=Customuser.Category.MODERATOR)
    if len(query) > 0:
        query.update(frozen=False)
        return redirect('users:unfreeze-view')
    else:
        return HttpResponseBadRequest("This is not a valid request")

@login_required(login_url='/users/login/')
@not_moderator_required
@not_frozen
def privilege_application(request):
    cust_err = None
    customuser = Customuser.objects.get(djangouser=request.user)
    if request.method == 'POST':
        if len(Application.objects.filter(djangouser=request.user)) > 0:
            return redirect('users:already-applied')
        form = ApplicationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['totype'] > customuser.usertype:
                application = form.save(commit=False)
                application.djangouser = request.user
                application.save()
                return render(request, 'users/apply-success.html', { 'application': application })
            else:
                cust_err = "Requested Privileges must be higher than current privilege"
    else:
        form = ApplicationForm()
    return render(request, 'users/apply.html', { 'form': form, 'cust_err': cust_err })

@login_required(login_url='/users/login/')
@not_moderator_required
@not_frozen
def already_applied(request):
    return render(request, 'users/already-applied.html')

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def grant_privilege(request):
    applications = Application.objects.all()
    return render(request, 'users/grant-privilege.html', { 'applications': applications })

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def grant_privilege_id(request, id):
    query = Application.objects.filter(pk=id)
    if len(query) > 0:
        customuser = Customuser.objects.filter(djangouser=query[0].djangouser)
        customuser.update(usertype=query[0].totype)
        query[0].delete()
        return redirect('users:grant-privilege')
    else:
        return HttpResponseBadRequest("This is not a valid request")

@login_required(login_url='/users/login/')
@moderator_required
@not_frozen
def reject_privilege_id(request, id):
    query = Application.objects.filter(pk=id)
    if len(query) > 0:
        query[0].delete()
        return redirect('users:grant-privilege')
    else:
        return HttpResponseBadRequest("This is not a valid request")
        


    
