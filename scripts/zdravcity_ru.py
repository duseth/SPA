import scrapy
import math
from scrapy.crawler import CrawlerProcess

from SPA_app.models import Medicine


class Spider(scrapy.Spider):
    name = "spider"
    start_urls = [
        'https://zdravcity.ru/c_lekarstvennye-preparaty/r_ulyanovsk/',
        'https://zdravcity.ru/c_bad/r_ulyanovsk/',
        'https://zdravcity.ru/c_medicinskie-izdelija/r_ulyanovsk/',
        'https://zdravcity.ru/c_medtehnika/r_ulyanovsk/',
        'https://zdravcity.ru/c_gigiena/r_ulyanovsk/',
        'https://zdravcity.ru/c_mama-i-malysh/r_ulyanovsk/',
        'https://zdravcity.ru/c_kosmetika/r_ulyanovsk/',
        'https://zdravcity.ru/c_zdorovoe-pitanie/r_ulyanovsk/'
    ]

    def parse(self, response, **kwargs):
        for n, url in enumerate(response.css('a.b-search-alphabet-first__title::attr(href)').extract(), 1):
            yield scrapy.Request(url=url, callback=self.get_urls_in_category)

    def get_urls_in_category(self, response):
        count_items: str = response.css('div.b-issue__title').css('span::text').extract_first()
        count_items = count_items.replace(' результатов', '')
        count_items = count_items.replace(' результата', '')
        count_items = count_items.replace(' результат', '')
        if count_items == '':
            count_items = '0'
        count_pages = math.ceil(int(count_items) / 21)
        if count_pages > 1:
            yield scrapy.Request(url=f'{response.url}?PAGEN_1=0', callback=self.parse_category)
            for i in range(2, count_pages + 1):
                yield scrapy.Request(url=f'{response.url}?PAGEN_1={i}', callback=self.parse_category)
        else:
            yield scrapy.Request(url=f'{response.url}?PAGEN_1=0', callback=self.parse_category)

    def parse_category(self, response):
        name = []
        price = []
        img = []
        url = []
        for i in response.css('a.b-product-item-new__title::text').extract():
            name.append(i.replace('\n', ''))

        temp = response.css('span.b-product-item-new__price--new-no-wrap').css('span::text').extract()
        for i in range(1, len(temp), 5):
            title_price = temp[i].replace('\n', '')
            price.append(title_price.replace('от ', ''))

        for i in response.css('a.b-product-item-new__image::attr(href)').extract():
            url.append(f'https://zdravcity.ru{i}')

        for i in response.css('picture').css('source.lazy::attr(data-srcset)').extract():
            img.append(f'https://zdravcity.ru{i}')
        del img[:3]
        for product in zip(name, price, url, img):
            if price != '':
                Medicine(title=product[0], photo=product[3], price=float(product[1]), url=product[2], pharmacy='zdravcity').save()


def run():
    process = CrawlerProcess(settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None
        },
    })
    process.crawl(Spider)
    process.start()
