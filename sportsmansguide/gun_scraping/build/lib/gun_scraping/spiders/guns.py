import re
import json
import scrapy
import urllib.parse
import requests

class GunsSpider(scrapy.Spider):
    name = "guns"

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
        token = self.settings.get('SCRAPE_KEY')
        print(token)
        list_urls = 'https://www.guns.com/catalog/search/listing?facets=%7B%22outlet%22:null,%22condition%22:null,%22compliance%22:%22%22,%22outletOnly%22:null%7D&facetGroup=%7B%22dealer%22:%22%22,%22product.upc%22:%22%22,%22product.rebates%22:%22%22,%22product.category%22:%22HANDGUNS,SHOTGUNS,RIFLES%22,%22product.collections%22:%22%22,%22product.subCategory%22:%22%22,%22product.manufacturer%22:%22%22,%22availability%22:%22In+stock%22%7D&page=1&filters=[]&sortBy=listing_weight'
        targetUrl = urllib.parse.quote(list_urls)
        data_url = f'https://api.scrape.do/?token={token}&url={targetUrl}'
        yield scrapy.Request(data_url, callback=self.parse)

    def parse(self,response):  
        token = self.settings.get('SCRAPE_KEY')  
        encoded_url = response.url
        decoded_urls = urllib.parse.unquote(encoded_url)
        decoded_url = decoded_urls.split('&url=')[-1]
        json_datas = json.loads(response.text)
        total_results_count = json_datas.get('totalResultsCount','')
        page_count = total_results_count // 24
        for page in range(1, page_count + 1):
            updated_target_url = re.sub(r'page=\d+', f'page={page}', decoded_url)
            targetUrl = urllib.parse.quote(updated_target_url)
            data_url = f'https://api.scrape.do/?token={token}&url={targetUrl}'
            yield scrapy.Request(data_url, callback=self.details)

    def details(self,response):
        
        json_datas = json.loads(response.text)
        for json_data in json_datas['firearms']:
            offer_url = 'https://www.guns.com' + json_data['link']
            vendor_url = 'https://www.guns.com/'
            upc  = ''
            upc = json_data.get('product','').get('upc','')
            if len(upc) ==12 and upc.isdigit():
                upc  = upc
            else:
                continue

            price = json_data.get('price','')
            if price != '':
               price =  float(price)
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
                self.api_value_add(data)
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