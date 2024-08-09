import scrapy
import json
import requests
import logging


class KygunSpider(scrapy.Spider):
    name ='kygun'


    Headers ={
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ta;q=0.7',
            'Origin': 'https://www.kygunco.com',
            'Referer': 'https://www.kygunco.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            }
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

    def start_requests(self):
        urls =["https://api.keenesdepot.io/kygunco.com/products?filters=Categories%2FId%3D%3D5&sorts=&page=1&pageSize=24","https://api.keenesdepot.io/kygunco.com/products?filters=Categories%2FId%3D%3D7&sorts=&page=1&pageSize=24",
                "https://api.keenesdepot.io/kygunco.com/products?filters=Categories%2FId%3D%3D3&sorts=&page=1&pageSize=24","https://api.keenesdepot.io/kygunco.com/products?filters=Categories%2FId%3D%3D51&sorts=&page=1&pageSize=24",
                "https://api.keenesdepot.io/kygunco.com/products?filters=Categories%2FId%3D%3D6&sorts=&page=1&pageSize=24"]
        for url in urls:
            yield scrapy.Request(url,headers=self.Headers,callback=self.parse,dont_filter=True)
            
    def parse(self, response):

        json_response = json.loads(response.text)
        total_product_count = json_response.get('totalItems','')
        listing_data_url = (response.url).split('pageSize')[0]
        api_url = f'{listing_data_url}pageSize={total_product_count}'
        yield scrapy.Request(api_url,headers=self.Headers,callback=self.listing_page_data)

    def listing_page_data(self, response):

        json_response = json.loads(response.text)
        datas = json_response.get('items', [])
        for data in datas:
            name = data.get('name')
            if 'silencer' in name.lower():
                continue
            else:
                
                instock =data.get('isInStock','')
                if instock:
                    item = {}
                    data_dict={}
                    product_url = data.get('slug', '')
                    item['offer_url'] = f'https://www.kygunco.com/product/{product_url}'
                    item['vendor_url'] = 'https://www.kygunco.com'
                    upc=(data.get('upc',''))
                    item['upc']  =''
                    if upc:
                        if len(upc) ==12 and upc.isdigit():
                            item['upc']  = data.get('upc','')
                        else:
                            continue
                    price_value = data.get('price')
                    if price_value is not None:
                        try:
                            item['price'] = float(price_value)
                        except (TypeError, ValueError):
                        
                            item['price'] = None 
                    else:
                        item['price'] = None  

                    data_dict['data'] = item 

                    if item['upc'] and item['price']:
                        self.api_value_add(data_dict)
                        yield data_dict
                        
                    else:
                        self.logger.warning(f'Mandatory Fields are Missing ----->{data_dict}\n')
                else:
                    continue

                    


                



                




