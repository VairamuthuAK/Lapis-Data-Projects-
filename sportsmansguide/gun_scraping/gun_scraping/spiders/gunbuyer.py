import scrapy
import requests

class GunBuyerSpider(scrapy.Spider):
    name = 'gunbuyer'

    not_pushed_count = 0
    api_added_count = 0

    start_urls = ['https://www.gunbuyer.com/firearms.html']

    headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                }

    def start_requests(self):
        self.crawler.stats.inc_value('API_pushed_item_count')
        self.crawler.stats.inc_value('API_not_pushed_item_count')
        for url in self.start_urls:
            yield scrapy.Request(url,callback=self.parse,headers=self.headers)

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

    def parse(self, response):
        url="https://www.gunbuyer.com/firearms.html?product_list_limit=30"
        decode_headers = { y.decode('ascii'): response.headers.get(y).decode('ascii') for y in response.headers.keys()}
        headers = self.headers
        decode_headers.update(headers)
        yield scrapy.Request(url, callback=self.parse_page,headers=decode_headers)
    
    def parse_page(self,response):
        next_page=response.xpath('//a[@class="action  next"]/@href').get('').strip()
        for block in response.xpath('//li[@class="item product product-item"]'):
            link=block.xpath('.//a[@class="product-item-link"]/@href').get('').strip()
            offer_url=link
            vendor_url='https://www.gunbuyer.com/'
            upc=block.xpath('.//form[@data-role="tocart-form"]/@data-product-sku').get('').strip()
            price=block.xpath('.//span[@data-price-amount]/@data-price-amount').get('').strip()
            if upc.isnumeric() and len(upc)==12:
                upc = int(upc)
            else:
                upc = None
            if upc and price:
                yield {'data':{
                'offer_url':offer_url,
                'vendor_url':vendor_url,
                'upc':upc,
                'price':float(price)
                }}
                data = {
                    "data": {
                        "offer_url": str(offer_url),
                        "vendor_url": "https://www.deguns.net/",
                        "upc": upc,
                        "price": float(price.replace(",", ""))
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
                        "upc": block.xpath('.//form[@data-role="tocart-form"]/@data-product-sku').get('').strip(),
                        "price": price
                    }
                }
                self.logger.warning(f'Mandatory Fields are Missing -----> \n{data}')
                self.not_pushed_count += 1
        if next_page:
            yield scrapy.Request(next_page, self.parse_page, headers=self.headers)
        self.crawler.stats.set_value('API_pushed_item_count',self.api_added_count)
        self.crawler.stats.set_value('API_not_pushed_item_count',self.not_pushed_count)
    
   
    
