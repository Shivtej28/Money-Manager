from decimal import Decimal
from django.shortcuts import render
from django.db.models import Sum
from datetime import date, timedelta, datetime
from transactions.models import Transaction
from django.contrib.auth.decorators import login_required


@login_required
def monthly_expense_report(request):
    today = date.today()

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date or not end_date:
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

    start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
    end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()

    transactions = Transaction.objects.filter(
        transaction_date__range=[start_date, end_date],
        user=request.user,
    )

    # Totals
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
    total_refund = (
        transactions.filter(subcategory__category_type="refund").aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )

    total_income = round(total_income, 2)
    total_expense = round(total_expense, 2)
    total_refund = round(total_refund, 2)

    adjusted_expense = round(total_expense - total_refund, 2)
    total_saving = round(total_income - adjusted_expense, 2)

    savings_rate = (total_saving / total_income * 100) if total_income > 0 else 0
    expense_percentage = (
        (adjusted_expense / total_income * 100) if total_income > 0 else 0
    )
    remaining_percentage = 100 - expense_percentage

    current_year = today.year
    available_years = list(range(current_year - 5, current_year + 1))

    category_expenses = (
        transactions.filter(subcategory__category_type="expense")
        .values("category__name")
        .annotate(total_spent=Sum("amount"))
        .order_by("-total_spent")[:20]
    )

    table_data = [
        {
            "rank": i + 1,
            "category": entry["category__name"],
            "amount": round(entry["total_spent"], 2),
            "percentage": (
                round((entry["total_spent"] / total_expense * 100), 2)
                if total_expense
                else 0
            ),
        }
        for i, entry in enumerate(category_expenses)
    ]

    context = {
        "selected_year": current_year,
        "total_income": total_income,
        "total_expense": adjusted_expense,
        "total_refund": total_refund,
        "total_saving": total_saving,
        "savings_rate": round(savings_rate, 2),
        "expense_percentage": round(expense_percentage, 2),
        "transactions": transactions,
        "months": [str(m) for m in range(1, 13)],
        "available_years": available_years,
        "remaining_percentage": round(remaining_percentage, 2),
        "table_data": table_data,
    }

    return render(request, "dashboard/monthly_expense.html", context)


def convert_decimal(value):
    if isinstance(value, Decimal):
        return round(float(value), 2)
    if isinstance(value, list):
        return [convert_decimal(v) for v in value]
    return value


@login_required
def yearly_report(request, selected_year=None):
    if not selected_year:
        selected_year = datetime.today().year

    available_years = Transaction.objects.dates("transaction_date", "year").distinct()

    transactions = Transaction.objects.filter(
        transaction_date__year=selected_year, user=request.user
    )

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
    total_refund = (
        transactions.filter(subcategory__category_type="refund").aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )

    adjusted_expense = round(total_expense - total_refund, 2)
    net_balance = round(total_income - adjusted_expense, 2)
    expense_percentage = (
        round((adjusted_expense / total_income) * 100, 2) if total_income else 0
    )

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

        refund = (
            transactions.filter(
                transaction_date__month=i, subcategory__category_type="refund"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        adjusted = expense - refund
        net_total = income - adjusted

        monthly_income.append(income)
        monthly_expense.append(adjusted)
        monthly_net_total.append(net_total)

        monthly_overview.append(
            {
                "month": month,
                "income": convert_decimal(income),
                "expense": convert_decimal(adjusted),
                "net_balance": convert_decimal(net_total),
            }
        )

    categories = (
        transactions.filter(subcategory__category_type="expense")
        .values("category__name")
        .annotate(total=Sum("amount"))
    )
    category_labels = [c["category__name"] for c in categories]
    category_values = [c["total"] for c in categories]

    context = {
        "year": selected_year,
        "available_years": [y.year for y in available_years],
        "total_income": convert_decimal(total_income),
        "total_expense": convert_decimal(adjusted_expense),
        "total_refund": convert_decimal(total_refund),
        "net_balance": convert_decimal(net_balance),
        "expense_percentage": convert_decimal(expense_percentage),
        "monthly_income": convert_decimal(monthly_income),
        "monthly_expense": convert_decimal(monthly_expense),
        "category_labels": category_labels,
        "category_values": convert_decimal(category_values),
        "remaining_percentage": convert_decimal(100 - expense_percentage),
        "monthly_overview": monthly_overview,
        "monthly_net_total": convert_decimal(monthly_net_total),
    }

    return render(request, "dashboard/yearly_report.html", context)
