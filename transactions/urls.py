from django.urls import path
from .views import (
    delete_transaction,
    update_transaction,
    transactions,
    create_transactions,
)

urlpatterns = [
    path("transactions/", transactions, name="transactions"),
    path("transactions/create", create_transactions, name="create_transactions"),
    path(
        "transactions/update/<int:transaction_id>/",
        update_transaction,
        name="update_transactions",
    ),
    path(
        "transactions/delete/<int:transaction_id>/",
        delete_transaction,
        name="delete_transactions",
    ),
]
