from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from users.decorators import not_frozen
from .models import Wallet, Transaction
from .forms import TransactionForm
from django.db.models import F
import decimal

# Create your views here.

@login_required(login_url='/users/login/')
@not_frozen
def accounts_home(request):
    try:
        wallet = Wallet.objects.get(owner=request.user)
    except Wallet.DoesNotExist:
        return HttpResponseBadRequest("<h2>Wallet does not exist for this account!</h2>")
    return render(request, 'accounts/wallet-home.html', { 'wallet': wallet })


@login_required(login_url='/users/login/')
@not_frozen
def coins_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            wallet = Wallet.objects.get(owner=request.user)
            new_transaction = form.save(commit=False)
            if decimal.Decimal(999999.00) - wallet.balance < new_transaction.amount:
                return render(request, 'accounts/add.html', { 'form': form, 'err': 'Maximum wallet limit exceeded!' })
            new_transaction.withdrawn = False
            new_transaction.person = request.user
            new_transaction.save()
            wallet.balance += new_transaction.amount
            wallet.save()
            return redirect('accounts:home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/add.html', { 'form': form, 'err': None })

@login_required(login_url='/users/login/')
@not_frozen
def coins_withdraw(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            wallet = Wallet.objects.get(owner=request.user)
            new_transaction = form.save(commit=False)
            if wallet.balance < new_transaction.amount:
                return render(request, 'accounts/remove.html', { 'form': form, 'err': 'You cannot withdraw more than what you have in your wallet!' })
            new_transaction.withdrawn = True
            new_transaction.person = request.user
            new_transaction.save()
            wallet.balance -= new_transaction.amount
            wallet.save()
            return redirect('accounts:home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/remove.html', { 'form': form, 'err': None })


@login_required(login_url='/users/login/')
@not_frozen
def transaction_history(request):
    history = Transaction.objects.filter(person=request.user)
    return render(request, 'accounts/history.html', { 'history': history })


