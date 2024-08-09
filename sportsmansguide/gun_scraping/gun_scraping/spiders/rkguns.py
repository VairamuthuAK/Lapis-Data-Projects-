import scrapy
import requests
import logging

class RkgunsSpider(scrapy.Spider):
    name = "rkguns"

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
            logging.info(f'Data append in api {api_response.text}')
        else:
            logging.warning(f'Not append in api {api_response.status_code}')
            logging.warning(f'Not Appended Payload --->\n{data}')

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': 'mage-cache-storage=%7B%7D; BVBRANDID=edae287b-7a06-400a-8540-15781cc696e6; _gid=GA1.2.1098237401.1721048243; ltkSubscriber-Footer=eyJsdGtDaGFubmVsIjoiZW1haWwiLCJsdGtUcmlnZ2VyIjoibG9hZCIsImx0a0VtYWlsIjoiIn0%3D; GSIDVt4v3zovVXoQ=6e935df2-a932-409f-bef8-82db69d5029a; STSIDVt4v3zovVXoQ=521efe6d-254a-4d77-9770-b605f4c7441a; ltkpopup-suppression-8917cfc9-28ca-475c-96dc-e3b0ac742eaf=1; _hjSessionUser_3334172=eyJpZCI6IjlhZDZmMzdmLTk3ZGYtNTExYi04ZWJkLTJiNDY5MmI4NzllNiIsImNyZWF0ZWQiOjE3MjEwNTA0NzEyMTYsImV4aXN0aW5nIjp0cnVlfQ==; form_key=NSFlYM2CZdbu8kvo; private_content_version=3845444212a9a00ae6ae5a9d39a8e530; aw_popup_viewed_page=%5B%22c67af9ee5ad41a7c9e7b7fc3ffea43996699a896afd656c06833beadee7bead5%22%2C%228d2356360de179d1bd20b290256661633efd156fe41bca62181493fa555042fa%22%2C%22a0a2d5645bc16ddb7a4428c08cac8a00c69e3755b351355a5ba5be95bb5d420b%22%2C%2223f0f7104eec2579a9291385ebdd3822a82e0d6d5b72e1c30576a4240c232d54%22%2C%227904a7b02271e83709172f9c98ef146542708bcb04f87b53becb9c9f2ff145b2%22%2C%22b843f0b2ff8b1b695855a5da6eb962f5d3929d2b22ed144b3e8a73f5eafc552a%22%2C%22977c30d911b563e780791aa801d241ce7f5d1c61fee6c27390dc606b1a4cab40%22%2C%22cef4f1632604bb13a0c9cb164d1ee53b7c82390b87cd08a8ca9b81221afbfe38%22%2C%22c181f91cbd487b70877592116ca8465306815ffa576ab571efb440dc35d1ef62%22%2C%220a2c071850da102b2571b818274b9cf8c0d45bd5e4979be6197f888a999e5c40%22%2C%2224e177241fd02ce6d2051e44ff1681e7adcd8574a998ce8b7031d4992d8a1ac8%22%2C%22445d5640888a454a9756d62002efa3c773114534bc4574da4bf863291fc3d34b%22%2C%22e6ff01bcacb2ff35e5ee34e5d874a6fe3b0ca3a06dc805a3d6556d53935c305e%22%2C%22a3979430beb79520af029be7db9b8360ae2fc4cffac29f546bb3d34a7372a41a%22%2C%224b53fec460b2e81ee5753eb9a19b0e0773798a24ef482642ef2cf28389d5e12e%22%2C%22b91484007579a0608247af658e9947859bfd447f3d0dedd0abcfea7a799e52fd%22%2C%22a637b36bac3b4ea97097fef31ee33fd3c9673befe48f81760b428734b66f63fc%22%2C%2268fce0688fddb3dfb21be20f786c3f830cad2e2cd71aa9e5e1bbfd623e397bec%22%2C%220a890f7f7ca40dc6f279a215ad7d3bae54cbc4d0d4f45cd84bc0cb0053f1e910%22%2C%2225352a929d43bcc7026b3704e90c3ee5e280cef3a4215c1ea5e2bcd4d9cc446c%22%2C%2268a662a439f4cccddfa000d53c21db38a88c503eefa45843bed6702590e9b0c8%22%2C%22af7ba56d6755d77fabeabdcb2b45f192d8422bd1e66868fa4c311fe30f074151%22%2C%22f1a187086ee5c7089457110055f43f02b7cfae515c78785dfc75ba844165adce%22%2C%22fe2c976413edaf0f2ce0b52115a9c4e6c023fcf75e320a1608d55e0ecc61f445%22%2C%22553f7feb9755af3afd9056b11fbdbe35d34b4b9f0ae03e5e4da4ffa10ed0c07f%22%2C%227c71638e213184c0dfc11538cb5205ee0002deb554834575bdb1f849f809cd02%22%2C%22e6e4edc6ca4883285e6a3dad4599141a8fe8c42cbbfd6f01a2e4b8e6e56e3c9e%22%2C%22e5428f210bfac30f2315ae435cace2e55d6eed3269ca92f6cbf72655f9762253%22%5D; PHPSESSID=hu4oh1a52mc0lvst4vv9osq0tq; klv_mage={"expire_sections":{"customerData":1721215902}}; _ga_M27XQSXFEV=GS1.1.1721215303.7.0.1721215303.60.0.0; BVBRANDSID=183b9df7-7263-42f9-8e78-4d4fc636ce28; mage-cache-storage-section-invalidation=%7B%7D; mage-cache-sessid=true; _ga=GA1.2.499052740.1721048243; _gat=1; mage-messages=; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; form_key=NSFlYM2CZdbu8kvo; ltkpopup-session-depth=16-2; _vuid=29a2b75f-f0a8-4f6a-8cbb-f299ecb1d1da',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
    
    def start_requests(self):
        urls =["https://www.rkguns.com/handguns.html?stock=1",
         "https://www.rkguns.com/rifles.html?stock=1",
         "https://www.rkguns.com/shotguns.html?stock=1"]
        for url in urls:
            yield scrapy.Request(url,callback=self.parse,headers=self.headers,meta={'proxy':self.proxy_scrape})
    
    def parse(self,response):
        for i in response.xpath('//ol[@class="filterproducts products list items product-items "]/li//a[@class="product-item-link"]'):
            data = i.xpath('./@href').get('')
            yield scrapy.Request(data,callback=self.parse_detail_data,headers=self.headers,meta={'proxy':self.proxy_scrape})

        if response.xpath('//li[@class="item pages-item-next"]/a[@title="Next"]/@href'):
            next_page = response.xpath('//li[@class="item pages-item-next"]/a[@title="Next"]/@href').get('')
            yield scrapy.Request(next_page,callback=self.parse,headers=self.headers,meta={'proxy':self.proxy_scrape})
            
    def parse_detail_data(self,response):
        item= {}
        offer_url = response.url
        vendor_url = 'https://www.rkguns.com/'
        title = response.xpath('//h1/span[@itemprop="name"]/text()').get('')
        upc = response.xpath('//th[contains(text(),"UPC")]/following-sibling::td/text()').get('').strip()
        price = response.xpath('//meta[@property="product:price:amount"]/@content').get('').strip()
        if title!='' and price and len(upc)>=12:
            item = {
            'data': {
                'offer_url': offer_url,
                'vendor_url': vendor_url,
                'upc': str(upc),  
                'price': float(price.replace(',',''))}
            }
            yield item
            data={
            'data': {
                'offer_url': offer_url,
                'vendor_url': vendor_url,
                'upc': str(upc),  
                'price': float(price.replace(',',''))}
            }
            self.api_value_add(data)
        
