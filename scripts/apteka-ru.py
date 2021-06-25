import json
import asyncio
import aiohttp

from SPA_app.models import Medicines

products: asyncio.Queue = asyncio.Queue()
headers: dict = {
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkNmM4ODQxZS1lYTg1LTQyMTQtYmQyOS1jMmFmMjI4Y"
                     "TE5MGEiLCJqdGkiOiI2MGQxYzEyY2I5MWEyYjZlOGEyNmUwMjkiLCJleHAiOjE2Mzk5MTEyMTIsIm5iZiI6MTYyNDM1OTIxMi"
                     "wicm9sZSI6IlNoYWRvd1VzZXIiLCJpYXQiOjE2MjQzNTkyMTJ9.ramDI6dp5Qmjt7owBbUYGk9ZenKRDOZEZQ1odlCMONbgcD"
                     "BIuna7LvRJR-8AdfzA0j2TEurwQDWNwMf8k3S_ybSEeiEllp6_MwcMyffSBnUomnX5QLhPR_XBS8ztQe8uWqN5G0EI66C-mes"
                     "loAvaNVinBXboBdg5FpPjdMFLz0SWkrsG8iNsyY-nd-Q_JKPPlu6ltr58SavtYsG592l3JCoXe13530jGWCUORfqRT09aFdoW"
                     "cMsqvHDbP8cU3NI7NV468SIzpY0qY8nb6_QZIX1vdS0z37kSv1PxUhBrkcsc62pBpSWngyHrcbrjOhQ8OVguapn6QYPBFOHSo"
                     "ZZL2bYUvpvmZ26_j5WWdCLiuH3ZggLdWHojxhFAYnTRi-4UqbGPyr-e6V2i9dQ2Zn0jq_JBtjb0rdpR9_QsSr87AQ-s0_C_0U"
                     "51ig3ThLd1ZMYaU87tipOHfX9Lez70Gm1Vn5mEj9A4xbNs2E-kC8y4VHx2MMxWsmq32WjRCatmu2vaPYQQovR2R0g476YATCV"
                     "WFigb4UXeq2c27IsASU3VlHaBQ_T2qCNkSPy4g_Bev2ld_8rM49l9n97dHLqF46ZgAFDo2etjBoZOwFHvJMdk2-kMXv_PMyZs"
                     "vejvKpGNhJjDlCTIvhMj9G-4CfXPb_MJGMhZvJ3nNm7wrp4gnkzvpF8",
}


async def get_products(category: str):
    current_page: int = 0
    products_is_over: bool = False

    async with aiohttp.ClientSession() as session:
        while not products_is_over:
            params: tuple = (
                ("url", category),
                ("page", str(current_page)),
                ("pageSize", "100"),
                ("catalogType", "GoodGroup"),
                ("goodRatingType", "View"),
                ("sortType", "Desc"),
            )

            async with session.get("https://api.apteka.ru/api/MonthlyRating/MonthlyGoods",
                                   headers=headers, params=params) as response:
                response_text: str = await response.text()
                try:
                    items: dict = json.loads(response_text)["result"]

                    for item in items:
                        photo = None
                        if item["photos"] is not None:
                            for photo_list in item["photos"]:
                                if photo_list is not None:
                                    photo = photo_list["original"]

                        product: dict = dict(
                            name=item["tradeName"],
                            price=int(item["minPrice"]),
                            photo=photo,
                            url="https://apteka.ru/product/" + item["humanableUrl"],
                        )

                        if product["price"] != 0:
                            products.put_nowait(product)
                    print(f"Page - {current_page:<3} | Category - {category:<5} | Total - {products.qsize():<6}")
                except:
                    products_is_over = True

            current_page += 1


def create_records():
    products_list: list = [products.get_nowait() for _ in range(products.qsize())]

    print(f"Creating {len(products_list)} rows of records...")
    Medicines.objects.bulk_create([
        Medicines(
            name=product["name"],
            photo=product["photo"],
            price=product["price"],
            url=product["url"],
            pharmacy="apteka.ru",
        )
        for product in products_list
    ])


async def main():
    categories: list = ["leka", "biol", "medi", "mib", "dets", "diet", "gigi", "dezi"]
    tasks = [asyncio.create_task(get_products(category)) for category in categories]

    await asyncio.gather(*tasks, return_exceptions=True)


def run():
    asyncio.run(main())
    create_records()
