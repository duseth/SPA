from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.core.paginator import Paginator, Page

from SPA.settings import MEILISEARCH_CLIENT


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def search(request: HttpRequest) -> HttpResponse:
    sort_list: dict = dict(name="по алфавиту", byprice="по возрастанию цены", bypricedesc="по убыванию цены")

    query = request.GET.get("query")
    if len(query) > 2:
        sort: str = request.GET.get("sort", default="name")
        page_number: int = int(request.GET.get("page", default=1))

        medicines: Page = __get_medicines(query, sort, page_number)

        return render(
            request, "search.html", {
                "medicines": medicines,
                "query": query,
                "sort_list": sort_list.items(),
                "sort": sort
            }
        )

    return redirect("SPA_app:index")


def pharmacies(request: HttpRequest) -> HttpResponse:
    return render(request, "pharmacies.html")


def contacts(request: HttpRequest) -> HttpResponse:
    return render(request, "contacts.html")


def __get_medicines(query: str, sort: str, page_number: int) -> Page:
    sort_list: dict = dict(name="title", byprice="price", bypricedesc="price")

    result: list = MEILISEARCH_CLIENT.index("medicines").search(query, {
        "attributesToHighlight": ["title"],
        "limit": 100000
    })["hits"][:300]
    result.sort(key=lambda item: item[sort_list.get(sort)], reverse=sort == "bypricedesc")

    paginator: Paginator = Paginator(result, 10)

    return paginator.get_page(page_number)
