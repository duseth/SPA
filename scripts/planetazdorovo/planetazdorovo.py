import asyncio
import json
from asyncio import CancelledError
from dataclasses import asdict
from typing import List

import aiohttp
from lxml import html
from lxml.html import HtmlElement

from SPA_app.models import Medicine
from .models import ItemModel
from .static import CATALOG_URL, DEFAULT_HEADERS, BASE_URL, DEFAULT_COOKIES
from .xpaths import *


def parse_price(price_str: str) -> float:
    return float(price_str.strip().split()[1])


async def parse_search_page(
    category_url: str,
    session: aiohttp.ClientSession,
    page: int,
    results_queue: asyncio.Queue,
) -> bool:
    params = {"PAGEN_1": page}
    response = await session.get(
        category_url, headers=DEFAULT_HEADERS, cookies=DEFAULT_COOKIES, params=params
    )
    print(response.status, response.url)
    page_tree: HtmlElement = html.fromstring(await response.text())
    for product_card in page_tree.xpath(product_card_xpath):
        if len(product_card.xpath(product_price_relative_xpath)) == 0:
            return False
        results_queue.put_nowait(
            ItemModel(
                url=BASE_URL + product_card.xpath(product_url_relative_xpath)[0],
                title=product_card.xpath(product_title_relative_xpath)[0],
                image_url=BASE_URL
                + product_card.xpath(product_image_url_relative_xpath)[0],
                price=parse_price(product_card.xpath(product_price_relative_xpath)[0]),
            )
        )
    return True


async def parse_category(
    category_url: str, session: aiohttp.ClientSession, results_queue: asyncio.Queue
):
    response = await session.get(
        category_url, headers=DEFAULT_HEADERS, cookies=DEFAULT_COOKIES
    )
    page_tree: HtmlElement = html.fromstring(await response.text())
    last_page = (
        int(page_tree.xpath(search_pagination_page_xpath)[-1])
        if len(page_tree.xpath(search_pagination_page_xpath))
        else 1
    )
    print(last_page)
    for page in range(1, last_page + 1):
        for _ in range(5):
            try:
                print(page)
                result = await parse_search_page(
                    category_url,
                    session=session,
                    page=page,
                    results_queue=results_queue,
                )
                if not result:
                    return
                break
            except:
                pass


async def main() -> List[ItemModel]:
    session = aiohttp.ClientSession()
    results_queue = asyncio.Queue()
    response = await session.get(CATALOG_URL, headers=DEFAULT_HEADERS)
    page_tree: HtmlElement = html.fromstring(await response.text())
    for category_url in page_tree.xpath(catalog_category_url_xpath):
        category_url = BASE_URL + category_url
        await parse_category(category_url, session, results_queue)
    products_list = [results_queue.get_nowait() for _ in range(results_queue.qsize())]
    await session.close()
    return products_list


def create_records(products: List[ItemModel]):
    print("bulk create")
    Medicine.objects.bulk_create([
        Medicine(
            title=product.title,
            photo=product.image_url,
            price=product.price,
            url=product.url,
            pharmacy="planetazdorovo",
        )
        for product in products
    ])


def run():
    products = asyncio.run(main())
    create_records(products)
