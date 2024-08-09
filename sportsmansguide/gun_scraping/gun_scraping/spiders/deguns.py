import re
import scrapy
import requests
import json
class DegunsSpider(scrapy.Spider):
    name = "deguns"
    
    start_urls = ["https://www.deguns.net/api/commerce/catalog/products-id?categoryId=84&includeOutOfStock=0&limit=50&brandId=","https://www.deguns.net/api/commerce/catalog/products-id?categoryId=148&includeOutOfStock=0&limit=50&brandId="]
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
    headers =  {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip',
                'referer': 'https://www.deguns.net/firearms',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
                }
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],headers=self.headers,callback=self.parse)

    def parse(self, response):
        datas=json.loads(response.text)
        for data in datas.get('data',{}).get('products'):
            url = response.urljoin(data.get('path',''))
            yield scrapy.Request(url,callback=self.parse_detail,headers=self.headers)
        next_page_flag = datas.get('data',{}).get('meta',{}).get('hasNextPage','')
        if next_page_flag:
            end_cursor = datas.get('data',{}).get('meta',{}).get('endCursor','')
            next_page_url = f'https://www.deguns.net/api/commerce/catalog/products-id?categoryId=84&includeOutOfStock=0&page={end_cursor}&limit=50&brandId='
            yield scrapy.Request(next_page_url,callback=self.parse,headers=self.headers)
        
    def parse_detail(self,response):
        data = {}
        data['offer_url'] = response.url
        data['vendor_url'] = 'https://www.deguns.net/'
        data['upc'] = ""
        data['price'] = ""
        if re.search('\"gtin12\"\:\"([^>]*?)\"',response.text):
            data['upc'] = re.findall('\"gtin12\"\:\"([^>]*?)\"',response.text)[0]
        price = response.xpath('//div[@class="sc-e255ad9a-0 jVzGy"]/text()').get('').replace('$','').replace(',','')
        if price:
            data['price'] = float(price)
        data_dict = {}
        data_dict['data'] = data
        if data['upc'] != ''and data['price'] != '':
            self.api_value_add(data_dict)
        else:
            self.logger.warning(f'Mandatory Fields are Missing ----->{data}\n')
        yield data_dict
       