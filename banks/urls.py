from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path("banks/", views.bank_list, name="banks"),
    path("bank/create", views.add_bank, name="add_bank"),
    path("bank/delete/<int:bank_id>/", views.delete_bank, name="delete_bank"),
    path("bank/update/<int:bank_id>/", views.update_bank, name="update_bank"),
]
