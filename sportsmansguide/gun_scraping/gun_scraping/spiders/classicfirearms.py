import requests
import scrapy
import urllib.parse
from scrapy.utils.project import get_project_settings

class ClassicfirearmsSpider(scrapy.Spider):
    name = "classicfirearms"
    proxy_scrape = 'http://brd-customer-hl_fb2f275a-zone-gunsnation-country-us:0ubeb589kvo2@brd.superproxy.io:22225'
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
        else:
            self.logger.warning(f'Not append in api {api_response.status_code}')
            self.logger.warning(f'Not Appended Payload --->\n{data}')
    start_urls = ["https://www.classicfirearms.com"]
    headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ta;q=0.8',
            'Accept-Encoding': 'gzip',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
    token = get_project_settings().get('SCRAPE_KEY')
    
    def start_requests(self):
        for start_url in self.start_urls:

            targeturl = urllib.parse.quote(start_url.strip())
            api_start_url = "http://api.scrape.do/?token={}&url={}".format(self.token, targeturl)
            yield scrapy.Request(api_start_url,headers=self.headers,callback=self.parse_link_collection)

    def parse_link_collection(self,response):
        for list_url_block in response.xpath('//ul[@class="mobile-sub rootmenu-list"]/li/div/div/ul/li/a'):
            list_url = list_url_block.xpath('./@href').get('')
            if '/long-guns/' in list_url or '/hand-guns/' in list_url:
                if '/long-guns/lower-receivers' not in list_url:
                    list_url = f'{list_url}?stock=1'
                    list_targeturl = urllib.parse.quote(list_url.strip())
                    api_list_url = "http://api.scrape.do/?token={}&url={}".format(self.token, list_targeturl)
                    yield scrapy.Request(api_list_url,headers=self.headers,callback=self.parse_list)
    def parse_list(self, response):
        for product in response.xpath('//h2[@class="product-name p-0 m-0"]/a'):
            product_url = product.xpath('./@href').get('')
            product_targeturl = urllib.parse.quote(product_url.strip())
            api_product_url = "http://api.scrape.do/?token={}&url={}".format(self.token, product_targeturl)
            yield scrapy.Request(api_product_url,headers=self.headers,callback=self.parse_detail,cb_kwargs={'product_url':product_url})
        if response.xpath('//a[@title="Next"]/@href'):
            next_page = response.xpath('//a[@title="Next"]/@href').get('')
            next_targeturl = urllib.parse.quote(next_page.strip())
            api_next_url = "http://api.scrape.do/?token={}&url={}".format(self.token, next_targeturl)
            yield scrapy.Request(api_next_url,headers=self.headers,callback=self.parse_list)
    def parse_detail(self,response,product_url):
        data = {}
        data['offer_url'] = product_url
        data['vendor_url'] = 'https://www.classicfirearms.com/'
        upc = response.xpath('//span[@class="upc-spacing"]/text()').get('')
        upc = upc.split(':')[1].strip() if ':' in upc else upc
        if upc.isnumeric() and len(upc) == 12:
            data['upc'] = upc
            price = response.xpath('//div[@class="price"]/text()|//span[@class="price"]/text()').get('').replace('$','').strip()
            decimal = response.xpath('//div[@class="price"]/span/text()|//span[@class="price"]/span/text()').get('00').strip()
            if price:
                if '.' not in price:
                    data['price'] = float(f"{price}.{decimal}".strip())
                else:
                    data['price'] = float(f"{price}".strip())
            else:
                data['price'] = ""
            data_dict = {}
            data_dict['data'] = data
            if data['upc'] != ''and data['price'] != '':
                self.api_value_add(data_dict)
            else:
                self.logger.warning(f'Mandatory Fields are Missing ----->{data}\n')
                
            yield data_dict
        else:
            self.logger.warning(f'upc fields contains alphanumeric or less the 12 char ----->{upc}\n')
