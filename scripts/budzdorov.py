from requests_html import HTMLSession

from SPA_app.models import Medicine

session = HTMLSession()
main_url = 'https://www.budzdorov.ru/'
urls = [
    'https://www.budzdorov.ru/category/2035',
    'https://www.budzdorov.ru/category/2036',
    'https://www.budzdorov.ru/category/2037',
    'https://www.budzdorov.ru/category/2038',
    'https://www.budzdorov.ru/category/2097',
    'https://www.budzdorov.ru/category/2112',
    'https://www.budzdorov.ru/category/2122',
    'https://www.budzdorov.ru/category/2129',
    'https://www.budzdorov.ru/category/2159',
    'https://www.budzdorov.ru/category/2252',
]

all_products = []


def get_data(s, url):
    try:
        response = s.get(url)
        response.html.render(sleep=5, timeout=20)
        page_count = response.html.find(
            'div.catalog-toolbar-pages__item.catalog-toolbar-pages__item_last', first=True)
        for page in range(1, int(page_count.text) + 1):
            parse_data_from_page(s, f'{url}?p={page}')
    except Exception as e:
        print(e)


def parse_data_from_page(s, url):
    response = s.get(url)
    response.html.render(sleep=5, timeout=20)
    product_list = response.html.find('div.product')
    for i, product in enumerate(product_list):
        product_data = {}
        product_data['photo'] = product.find(
            'img.product__img')[0].attrs['src']
        product_link = product.find('a.product__title')[0]
        exact_link = product_link.attrs['href']
        product_data['name'] = product_link.text
        product_data['url'] = f'{main_url}{exact_link}'
        product_data['price'] = product.find(
            'span.product__active-price-number')[0].text
        print(product_data)
        all_products.append(product_data)


def put_products_to_db():
    print("bulk create...")
    Medicine.objects.bulk_create(
        [
            Medicine(
                title=product["name"],
                photo=product["photo"],
                price=float(product["price"]),
                url=product["url"],
                pharmacy='rigla'
            )
            for product in all_products
        ]
    )


def run():
    for url in urls:
        get_data(session, url)
    put_products_to_db()
