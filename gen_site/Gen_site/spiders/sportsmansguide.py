import scrapy
import requests
import urllib.parse
from scrapy.utils.project import get_project_settings

class DackSpider(scrapy.Spider):
    name='sportsmansguide'
    settings = get_project_settings()
    token = settings.get('SCRAPE_KEY')
    
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
        url = 'https://www.sportsmansguide.com'
        targetUrl = urllib.parse.quote(url)
        data_url = f'https://api.scrape.do/?token={self.token}&url={targetUrl}'
        yield scrapy.Request(data_url,callback=self.parse)

    def parse(self,response):
        relative_links = response.xpath('//span[contains(text(), "Guns")]/ancestor::a/@href').get('')
        if relative_links:
            gen_link=f'https://www.sportsmansguide.com{relative_links}'
            targetUrl = urllib.parse.quote(gen_link)
            gen_url = f'https://api.scrape.do/?token={self.token}&url={targetUrl}'
            yield scrapy.Request(gen_url,callback=self.parse_category)

    def parse_category(self,response):
        for product in response.xpath('//div[@class="visual-nav-item-tile"]')[:3]:
            product_link = product.xpath('.//a/@href').get('')
            if product_link:
                catecory_link=f'https://www.sportsmansguide.com{product_link}&ipp=96#ipp'
                targetUrl = urllib.parse.quote(catecory_link)
                category_url = f'https://api.scrape.do/?token={self.token}&url={targetUrl}'
                yield scrapy.Request(category_url,callback=self.parse_sub_category)

    def parse_sub_category(self,response):
        for sub in response.xpath('//div[@class="product-tile"]'):
            sub_category_links=sub.xpath('.//a/@href').get('')
            if sub_category_links:
                sub_category_link = f'https://www.sportsmansguide.com{sub_category_links}'
                targetUrl = urllib.parse.quote(sub_category_link)
                sub_url = f'https://api.scrape.do/?token={self.token}&url={targetUrl}'
                yield scrapy.Request(sub_url,callback=self.parse_details,cb_kwargs={'sub_category_link':sub_category_link})
        #pagination
        next_page=response.xpath('//div[@class="paging-item next"]//a//@href').get('')
        if next_page:
            next_page_link = f'https://www.sportsmansguide.com{next_page}&ipp=96#ipp'
            targetUrl = urllib.parse.quote(next_page_link)
            next_page_link = f'https://api.scrape.do/?token={self.token}&url={targetUrl}'
            yield scrapy.Request(next_page_link,callback=self.parse_sub_category)

    def parse_details(self,response,sub_category_link):
        data={}
        data['offer_url'] = sub_category_link
        data['vendor_url'] = 'https://www.sportsmansguide.com/'
        upc = response.xpath('//span[@id="upc"]/text()').get('') 
        if upc:
            data['upc']=upc
        else:
            data['upc'] = ""
        
        price = response.xpath('//span[@class="regular-price"]/text()').get('').replace('$', '').replace(',', '').strip()
        if price:
            data['price'] = float(price)
        else:
            data['price'] = ""

        data_dict = {}
        data_dict['data'] = data
        if data['upc'] != ''and data['price'] != '':
            self.api_value_add(data_dict)
        else:
            self.logger.warning(f'Mandatory Fields are Missing ----->{data}\n')
        yield data_dict
