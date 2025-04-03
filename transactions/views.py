from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Transaction
from .forms import TransactionForm

# Create your views here.


@login_required
def transactions(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(
        request, "transactions/list_transactions.html", {"transactions": transactions}
    )


@login_required
def create_transactions(request):
    print("Helllloooo")
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect("transactions")
    else:
        form = TransactionForm(user=request.user)
    print("bfhdfbwdk")
    return render(request, "transactions/create_transaction.html", {"form": form})


@login_required
def update_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()  # This will trigger the updated balance logic in `save()`
            return redirect("transactions")
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(
        request,
        "transactions/create_transaction.html",
        {"form": form},
    )


@login_required
def delete_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    if request.method == "POST":
        transaction.delete()  # Deleting transaction updates balance
        return redirect("transactions")

    return render(
        request, "transactions/delete_transaction.html", {"transaction": transaction}
    )
