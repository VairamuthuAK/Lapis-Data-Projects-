import scrapy
import requests
import re

class BrownellsSpider(scrapy.Spider): 
    name = "brownells"

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

    def start_requests(self):
        str_links = [
        'https://www.brownells.com/guns/rifles/?facets=SpecialFilterTags%3AIn-stock&sort=AvgCustomerReview', 
        'https://www.brownells.com/guns/shotguns/?facets=SpecialFilterTags%3AIn-stock&sort=AvgCustomerReview', 
        'https://www.brownells.com/guns/handguns/?facets=SpecialFilterTags%3AIn-stock&sort=AvgCustomerReview',
        'https://www.brownells.com/guns/blackpowder/?facets=SpecialFilterTags%3AIn-stock&sort=AvgCustomerReview'
        ]
        for str_link in str_links:
            start_url = str_link
            headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,ta;q=0.6',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            yield scrapy.Request(url=start_url,headers = headers, callback=self.parse,meta={'proxy':self.proxy_scrape})
            
    def parse(self,response): 
        cat = response.url.split('/?')[0].split('/')[-1]
        count = response.xpath('//span[@data-auto-name="plp-totalcount-product-isD"]/text()').get('')
        count = int(count)
        pagination = count / 32
        next_page = round(pagination)
        if next_page:
            for nex in range(1, next_page + 1):
                guns = f'https://www.brownells.com/guns/{cat}/?facets=SpecialFilterTags%3AIn-stock&page={nex}&sort=AvgCustomerReview'
                headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,ta;q=0.6',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
                }
                yield scrapy.Request(url=guns,headers=headers, callback=self.pagination,meta={'proxy':self.proxy_scrape})

    
    def pagination(self,response):
        links = response.xpath('//div[@class="category-slider__item pl-item col-xl-4 col-6"]/a/@href').getall()
        for link in links:
            guns = f"https://www.brownells.com{link}"
            headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,ta;q=0.6',
            'referer': f'{response.url}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            yield scrapy.Request(url=guns, headers=headers,callback=self.parse_guns,meta={'proxy':self.proxy_scrape})
            
    def parse_guns(self, response):
        skus = re.findall(r'"sku":"(\d+)"', response.text)
        for sku in skus:
            url = f'{response.url}?sku={sku}'
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,ta;q=0.6',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            yield scrapy.Request(url, headers=headers, callback=self.final,meta={'proxy':self.proxy_scrape})

    def final(self, response):
        if response.xpath('//div[contains(text(), "No longer available")]'):
            logging.info(f'out_of_stock---------------------->',response.url)
            pass
        else:
            offer_url = response.url
            vendor_url = 'https://www.brownells.com'  
            upc = response.xpath('//div[@class="pdp-info__attr-item pdp-info__attr-upc flex-center"]//div[@class="pdp-info__attr-value"]/text()').get('').strip()
            price = response.xpath('//div[@class="pdp-info__price"]/span[contains(@class, "pdp-info__price-cost")]/text()').get('').strip()

            if upc:
                if len(upc) == 12 and upc.isdigit():
                    upc_valid = upc
                else:
                    return 
            else:
                upc_valid = ''

            if price:
                price = price.replace('$', '').replace(',', '')
                try:
                    price = float(price)
                except ValueError:
                    price = None
            else:
                price = None

            
            if upc_valid != '' and price != None:
                data={
                    "data": {
                        "offer_url": offer_url,
                        "vendor_url": vendor_url,
                        "upc": upc_valid,
                        "price": price
                    }
                }
                self.api_value_add(data)
                yield data
            else:
                data={
                    "data": {
                        "offer_url": offer_url,
                        "vendor_url": vendor_url,
                        "upc": upc_valid,
                        "price": price
                    }
                }
                self.logger.warning(f'Mandatory Fields are Missing -----> \n{data}')