import scrapy
import requests
import urllib.parse
from scrapy.utils.project import get_project_settings



class DackSpider(scrapy.Spider):
    name='buds'
    headers = {
    'accept': 'text/html, */*; q=0.01',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }
    out_of_stock_count = 0
    settings = get_project_settings() 
    token = settings.get('SCRAPE_KEY')
    processed_urls = set()
    
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
        self.crawler.stats.inc_value('out_of_stock_count')
        links = [
        "https://www.budsgunshop.com/search.php/type/air+guns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/revolvers/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/derringers/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/pistols/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/handguns/exclusive/ca/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/handguns/exclusive/mass/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/handguns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/handguns/other/in_stock/cond/used",
        "https://www.budsgunshop.com/search.php/type/black+powder+pistols/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/black+powder+rifles/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/nfa+long+guns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/class+iii+shotguns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/nfa+rifles/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/class+iii+pistols/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/ar+rifles/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/target+%26+hunting+rifles/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/rifles/action/13086/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/rifles/action/32592/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/rifles/other/in_stock/cond/used",
        "https://www.budsgunshop.com/search.php/type/ak+rifles/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/hunting+%26+target+shotguns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/shotguns/action/32592/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/shotguns/action/29038/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/shotguns/action/13087/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/bullpup+shotguns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/double+barrel+shotguns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/tactical+shotguns/other/in_stock",
        "https://www.budsgunshop.com/search.php/type/other+shotguns/other/in_stock"
        ]

        for link in links:
            targetUrl = urllib.parse.quote(link.strip())
            url = "http://api.scrape.do/?token={}&url={}".format(self.token, targetUrl)
            cat_url = link.split('type/')[-1].replace('/other/in_stock','').strip()
            yield scrapy.Request(url,headers=self.headers,callback=self.parse,cb_kwargs={'cat_url':cat_url,'link':link})

    def parse(self,response,cat_url,link):
        no_result = response.xpath('//span[@class="search_note"]/text()').get()
        if no_result:
            self.logger.info(f'no_result_url------------>{link}')
            pass
        else:
            count = response.xpath('//div[@class="col-xs-6 col-sm-3 col-md-2 search_total_results"]/text()').get('').strip()
            if count:
                total_count = count.replace('total results','').replace('most relevant results','').strip()
                count = int(total_count)
                if count < 1000:
                    cal = count/36
                    pagination = round(cal)
                    if pagination > 1:
                        for next in range(1,pagination+1):
                            pagination_url = f'https://www.budsgunshop.com/search.php/type/{cat_url}/page/{next}'
                            pagination_url = urllib.parse.quote(pagination_url)
                            url = "http://api.scrape.do/?token={}&url={}".format(self.token, pagination_url)
                            yield scrapy.Request(url,headers=self.headers,callback=self.final,cb_kwargs={'pagination_url':pagination_url})
                    else:
                        yield scrapy.Request(response.url,headers=self.headers,callback=self.final,cb_kwargs={'pagination_url':None})

                else:
                    minp = 1
                    maxp = 200
                    increment = 200

                    while True:
                        url = f"https://www.budsgunshop.com/search.php/type/{cat_url}/minp/{minp}/maxp/{maxp}"
                    
                        if maxp < 6000:
                            increment = 200
                        elif maxp < 10000:
                            increment = 500
                        else:
                            increment = 1000
                        
                        minp = maxp + 1
                        maxp += increment
                        if maxp > 21000: 
                            break
                        frame_url = urllib.parse.quote(url)
                        filter_url = "http://api.scrape.do/?token={}&url={}".format(self.token, frame_url)
                        yield scrapy.Request(filter_url,headers=self.headers,callback=self.pagination,cb_kwargs={'url':url})


    def pagination(self,response,url):
        status = response.xpath('//span[@class="search_note"]/text()').get()
        if status:
            self.logger.info(f'no_result_url------------>{url}')
            pass
        else:
            count = response.xpath('//div[@class="col-xs-6 col-sm-3 col-md-2 search_total_results"]/text()').get('').strip()
            if count:
                total_count = count.replace('total results','').replace('most relevant results','').strip()
                count = int(total_count)
                cal = count/36
                pagination = round(cal)
                if pagination > 1:
                    for next in range(1,pagination+1):
                        pagination_url = f'{url}/page/{next}'
                        pagination_url = urllib.parse.quote(pagination_url)
                        frame_url = "http://api.scrape.do/?token={}&url={}".format(self.token, pagination_url)
                        yield scrapy.Request(frame_url,headers=self.headers,callback=self.final,cb_kwargs={'pagination_url':pagination_url})
                else:
                    yield scrapy.Request(response.url,headers=self.headers,callback=self.final,cb_kwargs={'pagination_url':None})


        
    def final(self, response, pagination_url):
        status = response.xpath('//span[@class="search_note"]/text()').get()
        if status:
            self.logger.info(f'no_result_url------------>{pagination_url}')
            pass
        else:
            item = {}
            blocks = response.xpath('//div[@class="list-products"]')
            for block in blocks:
                offer_url = block.xpath('.//a[@class="list-products-name bgfont"]/@href').get('').strip()
                full_offer_url = response.urljoin(offer_url)
                
                if full_offer_url in self.processed_urls:
                    self.logger.info(f'Duplicate URL skipped: {full_offer_url}')
                    continue
                self.processed_urls.add(full_offer_url)
                
                if block.xpath('//span[@class="out-of-stock"]'):
                    self.out_of_stock_count += 1
                    self.logger.info(f'out_of_stock_url---------->{full_offer_url}')
                    continue
                
                try:
                    json_item = {}
                    item['offer_url'] = full_offer_url
                    item['vendor_url'] = 'https://www.budsgunshop.com/'
                    upc = block.xpath('./meta[@itemprop="gtin"]/@content').get('').strip()
                    if upc.isdigit():
                        item['upc'] = upc   
                    else:
                        continue
                    
                    price = block.xpath('.//span[@itemprop="price"]/text()').get('').strip().replace(',', '')
                    item['price'] = float(price)
                    json_item['data'] = item
                    if item['price'] and item['upc']:
                        self.api_value_add(json_item)
                        yield json_item
                    else:
                        self.logger.warning(f'Mandatory Fields are Missing ----->{json_item}\n')
                except Exception as e:
                    self.logger.error(f'Error processing block: {e}')
                    self.logger.info(f'invalid_price_link------------->{full_offer_url}')
                    continue

            self.crawler.stats.set_value('out_of_stock_count', self.out_of_stock_count)
