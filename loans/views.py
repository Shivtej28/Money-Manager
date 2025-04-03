from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Loan, InterestRateHistory
from .forms import LoanForm, InterestRateUpdateForm
from transactions.models import Transaction


@login_required
def loan_list(request):
    """List all loans for the logged-in user."""
    loans = Loan.objects.filter(user=request.user)
    return render(request, "loans/loan_list.html", {"loans": loans})


@login_required
def add_loan(request):
    """Add a new loan with initial interest rate."""
    if request.method == "POST":
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.save()

            # Add initial interest rate entry
            InterestRateHistory.objects.create(
                loan=loan, interest_rate=loan.interest_rate, start_date=loan.start_date
            )

            return redirect("loan_list")
    else:
        form = LoanForm()
    return render(request, "loans/add_loan.html", {"form": form})


@login_required
def loan_detail(request, loan_id):
    """Show loan details including transactions, interest history, and calculations."""
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    # Get all transactions related to this loan
    transactions = Transaction.objects.filter(subcategory=loan.category)

    # Calculate total amount paid (EMIs + Prepayments)
    total_paid = loan.total_paid()

    # Calculate remaining principal
    remaining_principal = loan.remaining_principal()

    # Calculate total interest payable (assuming simple formula)
    total_interest = loan.total_interest()

    # Calculate interest paid so far
    interest_paid = loan.total_interest_paid()

    # Calculate remaining interest
    remaining_interest = loan.remaining_interest()

    # Determine remaining tenure (months)
    remaining_tenure = loan.remaining_tenure()

    # Loan status
    loan_status = "Completed" if remaining_principal <= 0 else "Ongoing"

    # Get current interest rate
    current_interest_rate = loan.interest_rate

    # Get interest rate history
    interest_history = InterestRateHistory.objects.filter(loan=loan).order_by(
        "-start_date"
    )

    return render(
        request,
        "loans/loan_detail.html",
        {
            "loan": loan,
            "transactions": transactions,
            "total_paid": total_paid,
            "remaining_principal": remaining_principal,
            "total_interest": total_interest,
            "total_interest_paid": interest_paid,
            "remaining_interest": remaining_interest,
            "remaining_tenure": remaining_tenure,
            "loan_status": loan_status,
            "current_interest_rate": current_interest_rate,
            "interest_history": interest_history,
        },
    )


from datetime import date


@login_required
def loan_update(request, loan_id):
    """Update loan details, excluding interest rate."""
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    if request.method == "POST":
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.save()
            return redirect("loan_list")
    else:
        form = LoanForm(instance=loan)

    return render(request, "loans/add_loan.html", {"form": form, "loan": loan})


@login_required
def update_interest_rate(request, loan_id):
    """Allows users to update the interest rate for an existing loan."""
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    if request.method == "POST":
        form = InterestRateUpdateForm(request.POST)
        if form.is_valid():
            interest_rate_history = form.save(commit=False)
            interest_rate_history.loan = loan
            interest_rate_history.start_date = date.today()  # Ensure it's set correctly
            interest_rate_history.save()
            return redirect("loan_detail", loan_id=loan.id)
    else:
        form = InterestRateUpdateForm()

    return render(
        request, "loans/update_interest_rate.html", {"form": form, "loan": loan}
    )


@login_required
def loan_delete(request, loan_id):
    """Delete a loan after user confirmation."""
    loan = get_object_or_404(Loan, id=loan_id)

    if request.method == "POST":
        loan.delete()
        return redirect("loan_list")

    return render(request, "loans/loan_confirm_delete.html", {"loan": loan})
