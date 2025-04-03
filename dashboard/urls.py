from django.urls import path
from .views import monthly_expense_report, yearly_report

urlpatterns = [
    path("dashboard/", monthly_expense_report, name="dashboard"),
    path(
        "dashboard/yearly_report/<int:selected_year>",
        yearly_report,
        name="yearly_report",
    ),
    path(
        "dashboard/yearly_report/",
        yearly_report,
        name="yearly_report",
    ),
]
