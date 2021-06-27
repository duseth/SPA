import os
import json
import asyncio
import aiohttp

from SPA_app.models import Medicine


async def get_products(products: asyncio.Queue, categories: asyncio.Queue):
    headers: dict = {"Authorization": os.getenv("APTEKA_RU_AUTHORIZATION")}

    async with aiohttp.ClientSession() as session:
        while True:
            current_page: int = 0
            products_is_over: bool = False
            category: str = await categories.get()

            while not products_is_over:
                params = (
                    ("pageSize", "100"),
                    ("page", str(current_page)),
                    ("apiUrl", "/Search/CategoryUrl"),
                    ("categoryUrl", category)
                )

                async with session.get("https://api.apteka.ru/Search/CategoryUrl", headers=headers,
                                       params=params) as response:
                    products_is_over = __products_processing(products, await response.text())

                    print(f"Page - {current_page:<3} | Category - {category:<5} | Total - {products.qsize():<6}")
                    current_page += 1

            categories.task_done()
            if categories.qsize() == 0:
                break


def __products_processing(products: asyncio.Queue, response_text: str) -> bool:
    try:
        items: dict = json.loads(response_text)["result"]

        [products.put_nowait(product) for product in __get_products_from_page(items)
         if product["price"] != 0]

    except:
        return True

    return False


def __get_categories_queue() -> asyncio.Queue:
    categories_queue: asyncio.Queue = asyncio.Queue()

    with open("scripts/categories.json", "r") as file:
        categories: dict = json.load(file)

    for category, subcategories in categories.items():
        for subcategory in subcategories:
            categories_queue.put_nowait(category + "/" + subcategory)

    return categories_queue


def __get_medicine_photo(item: dict) -> str:
    if item is not None:
        for photo_list in item:
            if photo_list is not None:
                return photo_list.get("original")


def __get_products_from_page(items: dict) -> list:
    products: list = list()

    for item in items:
        products.append(
            dict(
                name=item["tradeName"],
                price=item["minPrice"],
                photo=__get_medicine_photo(item["photos"]),
                url="https://apteka.ru/product/" + item["humanableUrl"]
            )
        )

    return products if len(products) != 0 else None


async def main():
    products: asyncio.Queue = asyncio.Queue()
    categories: asyncio.Queue = __get_categories_queue()

    tasks = [asyncio.create_task(get_products(products, categories)) for _ in range(10)]
    await asyncio.gather(*tasks, return_exceptions=True)

    products_list: list = [products.get_nowait() for _ in range(products.qsize())]

    return products_list


def create_records(products):
    print(f"Creating {len(products)} rows of records...")
    Medicine.objects.bulk_create([
        Medicine(
            title=product["name"],
            photo=product["photo"],
            price=product["price"],
            url=product["url"],
            pharmacy="apteka.ru",
        )
        for product in products
    ])


def run():
    products = asyncio.run(main())
    create_records(products)
