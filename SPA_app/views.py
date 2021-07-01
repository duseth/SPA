from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest

from typing import Tuple, List, Dict
from SPA.settings import MEILISEARCH_CLIENT


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def search(request: HttpRequest) -> HttpResponse:
    sort_list: dict = dict(name="по алфавиту", byprice="по возрастанию цены", bypricedesc="по убыванию цены")

    query = request.GET.get("query")
    if len(query) > 2:
        sort: str = request.GET.get("sort", default="name")
        page: int = int(request.GET.get("page", default=1))
        medicines, medicines_num = __get_medicines(query, sort, page)

        return render(
            request, "search.html", {
                "medicines": medicines,
                "query": query,
                "sort_list": sort_list.items(),
                "sort": sort,
                "page": page,
                "num_pages": int(medicines_num / 10),
                "medicines_num": medicines_num
            }
        )

    return redirect("SPA_app:index")


def pharmacies(request: HttpRequest) -> HttpResponse:
    return render(request, "pharmacies.html")


def contacts(request: HttpRequest) -> HttpResponse:
    return render(request, "contacts.html")


def __get_medicines(query: str, sort: str, page: int) -> Tuple[List[Dict], int]:
    index_by_sort: dict = dict(name="medicines", byprice="medicines_byprice", bypricedesc="medicines_bypricedesc")

    result = MEILISEARCH_CLIENT.index(index_by_sort.get(sort)).search(query, {
        "attributesToHighlight": ["title"],
        "offset": page * 10,
        "limit": 10
    })

    return result["hits"], result["nbHits"]
