import re
import scrapy
import requests
import urllib.parse

class ExampleSpider(scrapy.Spider):
    name = "palmettostatearmory"
    
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
            
    def regex(self, word):
        word = re.sub(r'\s+', ' ', word)
        word = word.replace('\n', ' ')
        return word
    
    def start_requests(self):
        urls = ["https://palmettostatearmory.com/guns/handguns.html?stock_filter=Show+Only+In+Stock",
        "https://palmettostatearmory.com/guns/shotguns.html?stock_filter=Show+Only+In+Stock",
        "https://palmettostatearmory.com/guns/rifles.html?stock_filter=Show+Only+In+Stock"]
        
        for url in urls:
            token = self.settings.get('SCRAPE_KEY')
            print(token)
            targetUrl = urllib.parse.quote(url)
            ping_url = "http://api.scrape.do/?token={}&url={}".format(token, targetUrl)
            yield scrapy.Request(ping_url,callback=self.parse) 

    def parse(self, response):
        for block in response.xpath('//ol[@class="products list items product-items"]/li'):
            offer_url = block.xpath('./div[@class="product-item-info"]/a/@href').get('').strip()
            token = self.settings.get('SCRAPE_KEY')
            targetUrl = urllib.parse.quote(offer_url)
            offer_ping = "http://api.scrape.do/?token={}&url={}".format(token, targetUrl)
            yield scrapy.Request(offer_ping,callback=self.parse_detail_data,cb_kwargs={'offer_url':offer_url})
        next_page = response.xpath('//a[@title="Next"]/@disabled')
        if next_page==[]:
            next_page = response.xpath('//a[@title="Next"]/@href').get('')
            token = self.settings.get('SCRAPE_KEY')
            targetUrl = urllib.parse.quote(next_page)
            next_ping = "http://api.scrape.do/?token={}&url={}".format(token, targetUrl)
            yield scrapy.Request(next_ping,callback=self.parse)
    def parse_detail_data(self,response,offer_url):
            vendor_url = 'https://palmettostatearmory.com'
            upc = response.xpath('//th[contains(text(),"UPC")]/following-sibling::td/text()').get('').strip()
            price = response.xpath('//meta[@property="product:price:amount"]/@content').get('').strip()
            item = {
            'data': {
                'offer_url': offer_url,
                'vendor_url': vendor_url,
                'upc': str(upc),  
                'price': float(price.replace(',',''))}
            }
            yield item
            if upc != '' and price != None and len(upc)>=12:
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