from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest

from .models import *


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query")
    sort = request.GET.get("sort", default="name")
    sort_list: dict = {
        value: name
        for value, name in
        zip(["name", "byprice", "bypricedesc"], ["по алфавиту", "по возрастанию цены", "по убыванию цены"])
    }

    if query != "":
        medicines = __get_medicines(query, sort)
        paginator = Paginator(medicines, 10)

        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)

        return render(request, "search.html", {"query": query, "sort_list": sort_list.items(), "sort": sort, "page": page})
    return redirect("SPA_app:index")


def pharmacies(request: HttpRequest) -> HttpResponse:
    return render(request, "pharmacies.html")


def contacts(request: HttpRequest) -> HttpResponse:
    return render(request, "contacts.html")


def __get_medicines(query: str, sort: str) -> list:
    sort_key: dict = dict(name="name", byprice="price", bypricedesc="-price")

    all_medicines = Medicines.objects.order_by(sort_key.get(sort))

    medicines = list()
    for medicine in all_medicines:
        if query.lower() in medicine.name.lower():
            medicines.append(medicine)

    return medicines
