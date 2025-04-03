from decimal import Decimal

from django.shortcuts import render
from django.db.models import Sum
from datetime import date, timedelta, datetime

from transactions.models import Transaction
from django.contrib.auth.decorators import login_required


@login_required
def monthly_expense_report(request):
    # Get the current month & year
    today = date.today()

    start_date = request.GET.get("start_date")  # Get multiple selected months
    end_date = request.GET.get("end_date")

    if not start_date or not end_date:
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")  # 30 days ago
        end_date = today.strftime("%Y-%m-%d")  # Today

    start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
    end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
    # Default to the current month if none selected
    # if not start_date or end_date:
    #     start_date = today
    #     end_date = today - timedelta(30)
    # Filter transactions for selected months and year
    transactions = Transaction.objects.filter(
        transaction_date__range=[start_date, end_date],
        user=request.user,
    )

    # Calculate totals
    total_income = (
        transactions.filter(subcategory__category_type="income").aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )
    total_expense = (
        transactions.filter(subcategory__category_type="expense").aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )
    total_saving = total_income - total_expense

    # Calculate percentages
    savings_rate = (total_saving / total_income * 100) if total_income > 0 else 0
    expense_percentage = (total_expense / total_income * 100) if total_income > 0 else 0
    remaining_percentage = 100 - expense_percentage
    # Available years (Last 5 years)
    current_year = today.year
    available_years = list(range(current_year - 5, current_year + 1))

    category_expenses = (
        transactions.filter(subcategory__category_type="expense")
        .values("category__name")
        .annotate(total_spent=Sum("amount"))
        .order_by("-total_spent")[:20]
    )

    # Prepare Data for Table
    table_data = [
        {
            "rank": i + 1,
            "category": entry["category__name"],
            "amount": entry["total_spent"],
            "percentage": (
                round((entry["total_spent"] / total_expense * 100), 2)
                if total_expense
                else 0
            ),
        }
        for i, entry in enumerate(category_expenses)
    ]

    # Context for the template
    context = {
        # "selected_months": selected_months,
        "selected_year": current_year,
        "total_income": total_income,
        "total_expense": total_expense,
        "total_saving": total_saving,
        "savings_rate": round(savings_rate, 2),
        "expense_percentage": round(expense_percentage, 2),  # Added for the report
        "transactions": transactions,
        "months": [str(m) for m in range(1, 13)],  # Months as list of strings
        "available_years": available_years,
        "remaining_percentage": remaining_percentage,
        "table_data": table_data,
    }

    return render(request, "dashboard/monthly_expense.html", context)


def convert_decimal(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):  # Handle lists with Decimal values
        return [convert_decimal(v) for v in value]
    return value


# Assuming convert_decimal is defined


@login_required
def yearly_report(request, selected_year=None):
    if not selected_year:
        selected_year = datetime.today().year
    # Get available years for dropdown
    available_years = Transaction.objects.dates("transaction_date", "year").distinct()
    print(selected_year)
    # Filter transactions for the selected year
    transactions = Transaction.objects.filter(
        transaction_date__year=selected_year, user=request.user
    )

    # Calculate total income, expenses, and net balance
    total_income = (
        transactions.filter(subcategory__category_type="income").aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )
    total_expense = (
        transactions.filter(subcategory__category_type="expense").aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )
    net_balance = total_income - total_expense

    # Calculate expense percentage
    expense_percentage = (
        round((total_expense / total_income) * 100, 2) if total_income else 0
    )

    # Monthly breakdown
    monthly_income = []
    monthly_expense = []
    monthly_overview = []
    monthly_net_total = []

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    for i, month in enumerate(months, start=1):
        income = (
            transactions.filter(
                transaction_date__month=i, subcategory__category_type="income"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        expense = (
            transactions.filter(
                transaction_date__month=i, subcategory__category_type="expense"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        net_total = income - expense

        monthly_income.append(income)
        monthly_expense.append(expense)
        monthly_net_total.append(net_total)
        monthly_overview.append(
            {
                "month": month,
                "income": convert_decimal(income),
                "expense": convert_decimal(expense),
                "net_balance": convert_decimal(income - expense),
            }
        )

    # Category-wise expense breakdown
    categories = (
        transactions.filter(subcategory__category_type="expense")
        .values("category__name")
        .annotate(total=Sum("amount"))
    )
    category_labels = [c["category__name"] for c in categories]
    category_values = [c["total"] for c in categories]

    # Context for template
    context = {
        "year": selected_year,
        "available_years": [y.year for y in available_years],
        "total_income": convert_decimal(total_income),
        "total_expense": convert_decimal(total_expense),
        "net_balance": convert_decimal(net_balance),
        "expense_percentage": convert_decimal(expense_percentage),
        "monthly_income": convert_decimal(monthly_income),
        "monthly_expense": convert_decimal(monthly_expense),
        "category_labels": category_labels,
        "category_values": convert_decimal(category_values),
        "remaining_percentage": convert_decimal(100 - expense_percentage),
        "monthly_overview": monthly_overview,  # Added for table
        "monthly_net_total": convert_decimal(monthly_net_total),
    }

    return render(request, "dashboard/yearly_report.html", context)
