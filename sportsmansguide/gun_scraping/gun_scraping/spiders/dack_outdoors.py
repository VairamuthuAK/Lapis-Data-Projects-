import scrapy
import requests
import re
import json
import time
import logging
import ast
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


class DackOutdoorSpider(scrapy.Spider):
    name = "dack_outdoor"

    not_pushed_count = 0
    api_added_count = 0
    duplicate_count = 0
    out_of_stock = 0

    product_urls = []

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

    def playright_listing(self, listing_url):
        try:
            self.listing_page = None
            logging.info(f'Going to collect API Data using Playwright -----> {listing_url}')
            with sync_playwright() as playwright:
                chromium = playwright.chromium # or "firefox" or "webkit".
                browser = chromium.launch(headless=True,proxy={'server':'http://brd.superproxy.io:22225','username':'brd-customer-hl_fb2f275a-zone-gunsnation-country-us','password':'0ubeb589kvo2'})
                context = browser.new_context(java_script_enabled=True,extra_http_headers={
                    'Accept-Encoding': 'gzip'
                })
                context.clear_cookies()     
                def handle_response(response): 
                    if ("/retail-store-controller?ajax=true&url_action=get_product_search_results&" in response.url):
                        self.listing_page = response.json()
                page = context.new_page()
                stealth_sync(page)
                # page.on("response", lambda response: asyncio.create_task(handle_response(response)))
                page.on("response", handle_response)
                page.goto(listing_url,wait_until='networkidle')
                page.wait_for_selector('#results_count_wrapper')
                time.sleep(15)
                if self.listing_page:
                    logging.info('Data Available with the networking API....')
                    browser.close()
                    return True
                else:
                    logging.info('Looking the data into HTML Page....')
                    content = page.content()
                    if re.search(r'productResults\s*\=\s*([\w\W]*?)\;\s*facetDescriptions',content,re.DOTALL):
                        logging.info('Regex Matched....')
                        self.listing_page = re.findall(r'productResults\s*\=\s*([\w\W]*?)\;\s*facetDescriptions',content,re.DOTALL)[0]
                        browser.close()
                        return True
                    else:
                        logging.info('Regex Not Matched....')
                        browser.close()
                        return False
        except Exception as e:
            logging.warning(f'Error occured in Playwright{str(e)}')
            return False

    def start_requests(self):
        self.crawler.stats.inc_value('API_pushed_item_count')
        self.crawler.stats.inc_value('API_not_pushed_item_count')
        self.crawler.stats.inc_value('duplicate_product_link_count')
        self.crawler.stats.inc_value('out_of_stock')
        url = 'https://quotes.toscrape.com/page/1/'
        yield scrapy.Request(url=url,callback=self.parse)
    
    def parse(self, response):
        urls = [
            'https://dackoutdoors.com/product-category/bolt-action-handguns',
            'https://dackoutdoors.com/product-category/break-action-handguns',
            'https://dackoutdoors.com/product-category/lever-action-handguns',
            'https://dackoutdoors.com/product-category/pistols',
            'https://dackoutdoors.com/product-category/starter-pistols',
            'https://dackoutdoors.com/product-category/tactical-pistols',
            'https://dackoutdoors.com/product-category/rifles',
            'https://dackoutdoors.com/product-category/tactical-rifles',
            'https://dackoutdoors.com/product-category/uppers',
            'https://dackoutdoors.com/product-category/shotguns',
            'https://dackoutdoors.com/product-category/tactical-shotguns',
            'https://dackoutdoors.com/product-category/other-firearms',
            'https://dackoutdoors.com/product-category/combo'
        ]
        for listing_url in urls:           
            listing_data = self.playright_listing(listing_url)
            if listing_data:
                logging.info(f'----> Got API Data from Playwright <---- : {listing_url}')
                if 'product_search_results' in self.listing_page:
                    logging.info('JSON Data Detected!!!')
                    if type(self.listing_page).__name__ != "dict":
                        json_listing = json.loads(self.listing_page)
                        self.listing_page = None
                    else:
                        json_listing = self.listing_page
                        self.listing_page = None
                    listing_full_data = json_listing['product_search_results']
                else:
                    logging.info('List of Elements Detected!!!')
                    cleaned_string = self.listing_page.replace(',,,,,',',"","","","",').replace(',,,,',',"","","",').replace(',,,', ',"","",').replace(',,',',"",').replace('true','True').replace('false','False')
                    self.listing_page = None
                    listing_full_data = ast.literal_eval(cleaned_string)
                for data in listing_full_data:
                    inventory_quantity = data[-4]
                    inventory_distributor = data[-1]
                    offer_url = 'https://dackoutdoors.com' + data[15].replace('\\/','/')
                    if inventory_quantity != 0 and inventory_distributor != 0:                        
                        if offer_url not in self.product_urls:
                            self.product_urls.append(offer_url)
                            vendor_url = 'https://dackoutdoors.com/'
                            upc_dump = data[5]
                            if re.search(r'\d{12}',upc_dump,re.DOTALL):
                                logging.info(f'>---- Contains 12 characters and no alpha numeric in the UPC ----< >> {offer_url} <<')
                                upc = upc_dump
                            else:
                                logging.info(f'>---- Does not match 12 characters and alpha numeric in the UPC ----< >> {offer_url} <<')
                                upc = ''
                            price = data[-6]
                            if price:
                                price = price.replace(',','')
                                if price != 'Call for Price':
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
                                logging.warning(f'Mandatory Fields are Missing -----> \n{data}')
                                self.not_pushed_count += 1
                        else:
                            logging.info(f'---x Duplicate Product Link Found x--- {offer_url}')
                            self.duplicate_count += 1
                    else:
                        logging.info(f'---x Out of stock x--- >>{offer_url}<<')
                        self.out_of_stock += 1
            else:
                logging.warning(f'----> No API Data from Playwright <---- : {listing_url}')
        self.crawler.stats.set_value('API_pushed_item_count',self.api_added_count)
        self.crawler.stats.set_value('API_not_pushed_item_count',self.not_pushed_count)
        self.crawler.stats.set_value('duplicate_product_link_count',self.duplicate_count)
        self.crawler.stats.set_value('out_of_stock',self.out_of_stock)