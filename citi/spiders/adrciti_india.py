from common.items import IndiaDataItem
from datetime import datetime
from io import BytesIO
import pandas as pd
import pdfplumber
import hashlib
import scrapy
import tabula
import re
import os

class AdrcitiIndiaSpider(scrapy.Spider):
    name = "adrciti_india"

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
        url = 'https://depositaryreceipts.citi.com/adr/common/linkpage.aspx?linkFormat=M&pageId=5&subpageid=168'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        yield scrapy.Request(url, callback=self.parse, headers=headers)

    def parse(self, response):
        self.crawler.stats.inc_value('no_record_count')
        self.crawler.stats.inc_value('total_record_count')
        link = response.xpath('//strong[contains(., "INDIA: Click here to access the information")]/parent::a/@href').get()
        yield scrapy.Request(link, callback=self.parse_details)

    def parse_details(self, response):
        if response.status == 200:
            pdf_file = BytesIO(response.body)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                    if re.search(r'Information\s*as\s*of\s*[^>]*?\n',str(text)):
                        try:
                            raw_date = re.findall(r'Information\s*as\s*of\s*([^>]*?)\n',str(text))[0]
                            format_date = datetime.strptime(raw_date, '%dth %B, %Y').strftime('%Y%m%d')
                        except Exception as e:
                            print("Error extracting date:", e)
                            format_date = None
                        try:
                            dfs = tabula.read_pdf(BytesIO(response.body), pages='all',multiple_tables=True,stream=True,)
                            df = pd.concat(dfs, ignore_index=True)
                            df.rename(columns={'Unnamed: 0':'issuer','Unnamed: 1':'isin','Ratio':'ratio_share','Head-Room':'head_room_drs','Head-Room.1':'head_room_shares','Share Reserved':'share_reserved'},inplace=True)
                            df = df.drop(0)
                            df.reset_index(drop=True,inplace=True)
                            total_items = len(df)
                            self.crawler.stats.set_value('no_record_count',self.no_record_count)
                            self.crawler.stats.set_value('total_record_count',total_items)
                            for index,row in df.iterrows():
                                item=IndiaDataItem()
                                item['issuer']=row['issuer']
                                item['isin']=row['isin']
                                item['ratio_share']=row['ratio_share']
                                item['head_room_drs']=row['head_room_drs']
                                item['head_room_shares']=row['head_room_shares']
                                item['share_reserved']=row['share_reserved']
                                scraped_date = datetime.today()
                                item['scraped_date'] = scraped_date.strftime('%Y%m%d')
                                all_values = [str(item[key]) for key in item if key != 'scraped_date']
                                hash_obj = hashlib.md5(('_'.join(all_values)).encode('utf-8'))
                                hash = hash_obj.hexdigest()
                                item['hash'] = hash
                                item['date'] = format_date
                                yield item
                        except Exception as e:
                            print("Error processing PDF:", e)
                            df = None
        else:
            self.log(f'Bad Response ---> {response.status}')
            self.no_record_count += 1
            self.crawler.stats.set_value('no_record_count',self.no_record_count)