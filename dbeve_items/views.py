from django.shortcuts import render
from .models import Categories, Groups, Types

# Create your views here.

def items(request):
    return render(request, "dbeve_items/items.html")


def all_categories(request):
    categories = Categories.objects.all()[:100]
    return render(request, "dbeve_items/all_categories.html", context={"categories": categories,})


def all_groups(request):
    groups = Groups.objects.all()[:100]
    return render(request, "dbeve_items/all_groups.html", context={"groups": groups,})


def all_types(request):
    types = Types.objects.all()[:100]
    return render(request, "dbeve_items/all_types.html", context={"types": types,})
