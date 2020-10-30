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
        return HttpResponse("Wallet does not exist for this account!")
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
                return HttpResponseBadRequest('Wallet balance cannot exceed 999999.00 coins. Please reduce your amount.')
            new_transaction.withdrawn = False
            new_transaction.person = request.user
            new_transaction.save()
            wallet.balance += new_transaction.amount
            wallet.save()
            return redirect('accounts:home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/add.html', { 'form': form })

@login_required(login_url='/users/login/')
@not_frozen
def coins_withdraw(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            wallet = Wallet.objects.get(owner=request.user)
            new_transaction = form.save(commit=False)
            if wallet.balance < new_transaction.amount:
                return HttpResponseBadRequest('You cannot withdraw more coins than what is available in your wallet.')
            new_transaction.withdrawn = True
            new_transaction.person = request.user
            new_transaction.save()
            wallet.balance -= new_transaction.amount
            wallet.save()
            return redirect('accounts:home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/remove.html', { 'form': form })


@login_required(login_url='/users/login/')
@not_frozen
def transaction_history(request):
    history = Transaction.objects.filter(person=request.user)
    return render(request, 'accounts/history.html', { 'history': history })


