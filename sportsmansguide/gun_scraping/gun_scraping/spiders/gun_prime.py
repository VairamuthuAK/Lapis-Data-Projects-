import scrapy
import re
import requests
import logging


class GunPrimeSpider(scrapy.Spider):
    name = "gun_prime"
    logger = logging.getLogger(__name__)
    headers = {
        'authority': 'gunprime.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://gunprime.com/categories/firearms',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6266.213 Safari/537.36 OPR/111.0.4728.118'
    }
    not_pushed_count = 0
    accessories_count = 0
    api_added_count = 0

    def api_value_add(self,data):
        api_url = 'https://dev-api.gunsnation.com/api/firearm-offers'
        api_token = self.settings.get('API_KEY')
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        api_response = requests.post(api_url, json=data, headers=headers)
        if api_response.status_code==200:
            self.logger.info(f'Data append in api ---->\n{api_response.text}')
            return True
        else:
            self.logger.warning(f'Not append in api {api_response.status_code}')
            self.logger.warning(f'Not Appended Payload --->\n{data}')
            return False

    def start_requests(self):
        self.crawler.stats.inc_value('API_pushed_item_count')
        self.crawler.stats.inc_value('API_not_pushed_item_count')
        self.crawler.stats.inc_value('accessories_item_count')
        url = 'https://gunprime.com/categories/firearms?page=1&per_page=96&search%5Bavailability%5D=in_stock&taxon=2'
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        for block in response.xpath('(//div[@id="products"])[1]//div[@class="panel-body text-center product-body"]'):
            product_link = response.urljoin(block.xpath('./a/@href').get('').strip())
            headers = {
                'authority': 'gunprime.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'referer': response.url,
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Debian; Linux; rv:127.0) Gecko/20210409 Firefox/127.0',
            }
            yield scrapy.Request(product_link,headers=headers,callback=self.product_detail)
        self.crawler.stats.set_value('API_pushed_item_count',self.api_added_count)
        self.crawler.stats.set_value('API_not_pushed_item_count',self.not_pushed_count)
        self.crawler.stats.set_value('accessories_item_count',self.accessories_count)
        next_page = response.xpath('//ul[@class="pagination "]/li[@class="next_page"]/a/@href').get('')
        if next_page:
            next_page_count = int(re.findall(r'\?page\=(.*?)\&',next_page,re.DOTALL)[0])
            page_ref = next_page_count - 1
            self.headers['referer'] = f'https://gunprime.com/categories/firearms?page={page_ref}&per_page=96&search%5Bavailability%5D=in_stock&taxon=2'
            yield scrapy.Request(url=response.urljoin(next_page),headers=self.headers,callback=self.parse)
    
    def product_detail(self, response):
        bread_crumbs_dump = response.xpath('//nav[@id="breadcrumbs"]//li/a/span/text()').getall()
        if ('Accessories' not in bread_crumbs_dump) and ('Receiver' not in bread_crumbs_dump):
            offer_url = response.url
            vendor_url = 'https://gunprime.com/'
            if re.search(r'UPC\:<\/span>\s*(.*?)\s*<',response.text,re.DOTALL):
                upc_dump = re.findall(r'UPC\:<\/span>\s*(.*?)\s*<',response.text,re.DOTALL)[0]
                if re.search(r'\d{12}',upc_dump,re.DOTALL):
                    self.logger.info(f'>---- Contains 12 characters and no alpha numeric in the UPC ----< >> {offer_url} <<')
                    upc = upc_dump
                else:
                    self.logger.info(f'>---- Does not match 12 characters and alpha numeric in the UPC ----< >> {offer_url} <<')
                    upc = ''
            else:
                upc = ''
            selling_price = response.xpath('//span[@class="lead price selling"]/@content').get()
            if selling_price:
                price = float(selling_price)
            else:
                price = response.xpath('//span[@class="lead original-price selling"]/@content').get()
                if price:
                    price = float(price)
                else:
                    price = None

            yield {
                "data": {
                    "offer_url": offer_url,
                    "vendor_url": vendor_url,
                    "upc": upc,
                    "price": price
                }
            }
            if upc != '' and price != None:
                data={
                    "data": {
                        "offer_url": offer_url,
                        "vendor_url": vendor_url,
                        "upc": upc,
                        "price": price
                    }
                }
                status = self.api_value_add(data)
                if status:
                    self.api_added_count += 1

            else:
                data={
                    "data": {
                        "offer_url": offer_url,
                        "vendor_url": vendor_url,
                        "upc": upc,
                        "price": price
                    }
                }
                self.logger.warning(f'Mandatory Fields are Missing -----> \n{data}')
                self.not_pushed_count += 1

        else:
            cates = ', '.join(bread_crumbs_dump)
            self.logger.info(f'Excluded Category Found ----> <{cates}>')
            self.accessories_count += 1