from django.shortcuts import render, redirect

from .models import Banks
from .forms import BankForm
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def bank_list(request):
    banks = Banks.objects.filter(user=request.user)
    return render(request, "banks/bank_list.html", {"banks": banks})


@login_required
def add_bank(request):
    if request.method == "POST":
        form = BankForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            print(request.user)
            bank.user = request.user
            bank.save()
            return redirect("banks")
    else:
        form = BankForm()
    return render(request, "banks/add_bank.html", {"form": form})


@login_required
def delete_bank(request, bank_id):
    bank = Banks.objects.get(id=bank_id)
    if request.method == "POST":
        bank.delete()
        return redirect("banks")
    else:
        return render(request, "banks/delete_bank.html", {"bank": bank})


@login_required
def update_bank(request, bank_id):
    bank = Banks.objects.get(id=bank_id)
    print(bank)
    form = BankForm(instance=bank)
    if request.method == "POST":
        print("In IF bblock")
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            return redirect("banks")
    return render(request, "banks/add_bank.html", {"form": form})
