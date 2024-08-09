from common.items import CitikoreanadrDataItem
from datetime import datetime
from io import BytesIO
import pandas as pd
import hashlib
import scrapy
import os


class AdrKoreanEquitiesExchangeSpider(scrapy.Spider):
    name = "adrkorean_equitiesexchange"

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
        url = 'https://www.ksd.or.kr/en/api/dr/drconversion/excel'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ta;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.ksd.or.kr/en/resource-center/dr/dr-conversion',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        yield scrapy.Request(url=url, headers=headers, callback=self.parse_excel)

    def parse_excel(self, response):
        if response.status == 200:
            df = pd.read_excel(BytesIO(response.body))
            final_df = df.fillna('')
            for index,row in final_df.iterrows():
                item=CitikoreanadrDataItem()
                item['issuer']=row['Issuer']
                item['class_of_stock']=row['Class of Stock']
                item['kr_isin']=row['KR ISIN']
                item['dr_isin']=row['DR ISIN']
                item['ratio_ord_dr']=row['Ratio(ORD:DR)']
                item['ceiling']=row['Ceiling']
                item['outstanding']=row['Outstanding']
                item['available']=row['Available']
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