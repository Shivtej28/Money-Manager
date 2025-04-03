from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category
from .forms import CategoryForm


# Create your views here.
@login_required
def list_categories(request):
    category_type = request.GET.get("category_type", "")

    # Fetch unique category types
    category_types = Category.objects.values_list("category_type", flat=True).distinct()

    # Filter categories if a category type is selected
    if category_type:
        categories = Category.objects.filter(
            category_type=category_type, user=request.user
        )
    else:
        categories = Category.objects.filter(user=request.user)

    return render(
        request,
        "categories/list_categories.html",
        {
            "categories": categories,
            "category_types": category_types,
        },
    )


@login_required
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect("list_categories")
    else:
        form = CategoryForm(user=request.user)

    return render(request, "categories/create_category.html", {"form": form})


@login_required
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == "POST":
        category.delete()
        return redirect("list_categories")
    else:
        return render(
            request, "categories/delete_categories.html", {"category": category}
        )


@login_required
def update_category(request, category_id):
    category = Category.objects.get(id=category_id)
    form = CategoryForm(instance=category, user=request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("list_categories")
    return render(request, "categories/create_category.html", {"form": form})
