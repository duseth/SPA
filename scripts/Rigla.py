from asyncio.tasks import sleep
import re
import asyncio
from requests_html import AsyncHTMLSession

from SPA_app.models import Medicines

session = AsyncHTMLSession()
main_url = 'https://ulyanovsk.rigla.ru'
urls = [
    'https://ulyanovsk.rigla.ru/cat/samoe-aktualnoe',
    'https://ulyanovsk.rigla.ru/cat/lekarstvennye-preparaty',
    'https://ulyanovsk.rigla.ru/cat/fitopreparaty',
    'https://ulyanovsk.rigla.ru/cat/vitaminy-i-bady',
    'https://ulyanovsk.rigla.ru/cat/planirovanie-semi',
    'https://ulyanovsk.rigla.ru/cat/mama-i-malysh',
    'https://ulyanovsk.rigla.ru/cat/medicinskie-izdeliya',
    'https://ulyanovsk.rigla.ru/cat/pribory-medicinskie',
    'https://ulyanovsk.rigla.ru/cat/gigiena-krasota-i-uhod',
    'https://ulyanovsk.rigla.ru/cat/sport-i-fitnes',
    'https://ulyanovsk.rigla.ru/cat/optika-i-kontaktnaya-korrekciya'
]

all_products = asyncio.Queue()


async def get_data(s, url):
    try:
        response = await s.get(url)
        await response.html.arender(sleep=2)
        page_count = response.html.find(
            'div.catalog-toolbar-pages__item.catalog-toolbar-pages__item_last', first=True)
        for page in range(1, int(page_count.text) + 1):
            await parse_data_from_page(s, f'{url}?p={page}', page)
    except Exception as e:
        print(e)


async def parse_data_from_page(s, url, page):
    response = await s.get(url)
    await response.html.arender(sleep=5)
    product_list = response.html.find('div.product')
    for i, product in enumerate(product_list):
        product_data = {}
        product_data['photo'] = product.find(
            'img.product__img')[0].attrs['data-src']
        product_link = product.find('a.product__title')[0]
        exact_link = product_link.attrs['href']
        product_data['name'] = product_link.text
        product_data['url'] = f'{main_url}{exact_link}'
        product_data['price'] = product.find(
            'span.product__active-price-number')[0].text
        all_products.put_nowait(product_data)


def put_products_to_db():
    products = [all_products.get_nowait() for _ in all_products.qsize()]

    Medicines.objects.bulk_create(
        [
            Medicines(
                title=product["name"],
                photo=product["photo"],
                price=product["price"],
                url=product["url"],
                pharmacy='rigla'
            )
            for product in products
        ]
    )


async def main():
    tasks = (get_data(session, url) for url in urls)
    return await asyncio.gather(*tasks)


def run():
    session.run(main)
    put_products_to_db()
