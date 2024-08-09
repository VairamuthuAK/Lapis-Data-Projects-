from common.items import TaiwanDataItem
from datetime import datetime
import hashlib
import scrapy
import os

class AdrCitiTwseSpider(scrapy.Spider):
    name = "adrciti_twse"

    current_date = datetime.now().strftime("%Y-%m-%d")

    no_record_count = 0

    custom_settings = {
        'ITEM_PIPELINES': {
            "common.pipelines.AdrCitiPipeline": 300,
        },
        'SLACK_ENABLED' : True,
        'FEED_EXPORT_ENCODING' : "utf-8",
        'FEEDS': {f"s3://{os.getenv('OUTPUT_BUCKET')}/output/daily_collections/citi/{current_date}/{name}.json": {"format": "json"}},
    }

    def start_requests(self):
        self.crawler.stats.inc_value('no_record_count')
        self.crawler.stats.inc_value('total_record_count')
        url='https://emops.twse.com.tw/server-java/t47hsc01_e?step=0&TYPEK=otc'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            }
        yield scrapy.Request(url,callback=self.parse,headers=headers)

    def parse(self,response):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day - 1
        url_1 ='https://emops.twse.com.tw/server-java/t47hsc01_e'
        payload = {
            'colorchg': '',
            'compTWO': '',
            'step': '1',
            'YEAR': str(year),
            'MONTH':str(month),
            'DAY': str(day)
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'null',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            }
        yield scrapy.FormRequest(url_1,callback=self.parse_details_callback,method="POST",formdata=payload,headers=headers,cb_kwargs = {'year': year,'month':month,'day':day})

    def parse_details_callback(self,response,day,year,month):
        if response.status ==200:
            total_items = len(response.xpath('//table[@align="center"]//tr').getall())
            blocks = response.xpath('//table[@align="center"]//tr')
            self.crawler.stats.set_value('no_record_count',self.no_record_count)
            self.crawler.stats.set_value('total_record_count',total_items)
            for value in blocks[1:]:
                item=TaiwanDataItem()
                day_str = f"{day:02}"
                month_str = f"{month:02}"
                item['input_date'] = f'{year}{month_str}{day_str}'
                item['market']=value.xpath('.//td[1]/text()').get('').strip()
                item['company_name']=value.xpath('.//td[2]/text()').get('').strip()
                item['isin_code']=value.xpath('.//td[3]/text()').get('').strip()
                item['place_where_overseas_depositary_receipts_to_be_listed']=value.xpath('.//td[4]/text()').get('').strip()
                item['name_of_the_depositary_institution']=value.xpath('.//td[5]/text()').get('').strip()
                item['local_agent']=value.xpath('.//td[6]/text()').get('').strip()
                item['total_issued_shares']=value.xpath('.//td[7]//text()').get('').strip()
                item['outstanding_shares']=value.xpath('.//td[8]//text()').get('').strip()
                item['total_reissuable_shares']=value.xpath('.//td[9]//text()').get('').strip()
                scraped_date = datetime.today()
                item['scraped_date'] = scraped_date.strftime('%Y%m%d')
                all_values = [str(item[key]) for key in item if key != 'scraped_date']
                hash_obj = hashlib.md5(('_'.join(all_values)).encode('utf-8'))
                hash = hash_obj.hexdigest()
                item['hash'] = hash
                yield item
        else:
            self.log(f'Bad Response ---> {response.status}')
            self.no_record_count += 1
            self.crawler.stats.set_value('no_record_count',self.no_record_count)