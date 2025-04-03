from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.list_categories, name="list_categories"),
    path("categories/create/", views.create_category, name="create_category"),
    path(
        "categories/delete/<int:category_id>/",
        views.delete_category,
        name="delete_category",
    ),
    path(
        "categories/update/<int:category_id>/",
        views.update_category,
        name="update_category",
    ),
]
