from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

from .models import *


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return search(request, request.POST.get("q"))
    return render(request, "index.html")


def search(request: HttpRequest, query: str):
    medicines = Medicines.objects.all()
    query_medicines = list()

    for medicine in medicines:
        if query.lower() in medicine.name.lower():
            query_medicines.append(medicine)

    return render(request, "search.html", {"medicines": query_medicines[:100]})
