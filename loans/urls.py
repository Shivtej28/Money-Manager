from django.urls import path
from .views import loan_list, add_loan, loan_detail, loan_update, loan_delete,update_interest_rate

urlpatterns = [
    path("loan/", loan_list, name="loan_list"),
    path("loan/add/", add_loan, name="add_loan"),
    path("loan/<int:loan_id>/", loan_detail, name="loan_detail"),
    path("loans/update/<int:loan_id>/", loan_update, name="loan_update"),
    path("loans/delete/<int:loan_id>/", loan_delete, name="loan_delete"),
     path("<int:loan_id>/update_interest/", update_interest_rate, name="update_interest_rate"),
]
