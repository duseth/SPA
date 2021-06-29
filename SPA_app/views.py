from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest

from .models import *


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query")
    sort = request.GET.get("sort", default="name")

    sort_names: dict = dict(
        name="по алфавиту", byprice="по возрастанию цены", bypricedesc="по убыванию цены")

    if len(query) > 2:
        medicines = get_medicines(query, sort)
        page = __get_current_page(
            medicines, request.GET.get("page", default=1))

        return render(
            request, "search.html",
            {
                "all_medicines": medicines,
                "query": query,
                "sort_list": sort_names.items(),
                "sort": sort,
                "page": page
            }
        )

    return redirect("SPA_app:index")


def pharmacies(request: HttpRequest) -> HttpResponse:
    return render(request, "pharmacies.html")


def contacts(request: HttpRequest) -> HttpResponse:
    return render(request, "contacts.html")


def get_medicines(query: str, sort: str) -> list:
    sort_keys: dict = dict(name="title", byprice="price", bypricedesc="-price")

    all_medicines = Medicine.objects.order_by(sort_keys.get(sort))

    medicines = list()
    for medicine in all_medicines:
        if query.lower() in medicine.title.lower():
            medicines.append(medicine)

    return medicines


def __get_current_page(medicines: list, page_number: int) -> Paginator:
    paginator = Paginator(medicines, 10)
    return paginator.get_page(page_number)
