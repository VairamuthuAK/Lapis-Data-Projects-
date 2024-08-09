from common.items import CitiCorporateItem
from datetime import datetime
from io import BytesIO
import pandas as pd
import hashlib
import scrapy
import os


class AdrCitiCorporateSpider(scrapy.Spider):
    name = "adrciti_corporate"

    no_record_count = 0

    current_date = datetime.now().strftime("%Y-%m-%d")

    custom_settings = {
        'ITEM_PIPELINES': {
            "common.pipelines.AdrCitiPipeline": 300,
        },
        'SLACK_ENABLED' : True,
        'FEED_EXPORT_ENCODING' : "utf-8",
        'FEEDS': {f"s3://{os.getenv('OUTPUT_BUCKET')}/output/daily_collections/citi/{current_date}/{name}.json": {"format": "json"}},
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://depositaryreceipts.citi.com',
        'Pragma': 'no-cache',
        'Referer': 'https://depositaryreceipts.citi.com/adr/notices/corpActions.aspx?pageId=8&subpageid=6',
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
        
    def start_requests(self):
        self.crawler.stats.inc_value('no_record_count')
        self.crawler.stats.inc_value('total_record_count')
        url = 'https://depositaryreceipts.citi.com/adr/notices/corpActions.aspx?pageId=8&subpageid=6'
        yield scrapy.Request(url,callback=self.parse,dont_filter =True) 
    
    def datetime_format(self,timedata):
        if timedata:
            try:
                if '-' in timedata:
                    date_obj = datetime.strptime(timedata, '%Y-%m-%d')
                elif '/' in timedata:
                    date_obj = datetime.strptime(timedata, '%m/%d/%Y')
                return date_obj.strftime("%Y%m%d")
            except ValueError:
                print(f"Unrecognized date format: {timedata}")
                return ''
        else:
            return ''

    def parse(self, response):
        view_state = response.xpath('//input[@name="__VIEWSTATE"]/@value').get('').strip()
        view_state_generator = response.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').get('').strip()
        event_validation = response.xpath('//input[@name="__EVENTVALIDATION"]/@value').get('').strip()
        inpt_txtSearch = response.xpath('//input[@name="ctl00$inpt_txtSearch"]/@value').get('').strip()
        earchclsymb = response.xpath('//input[@name="ctl00$searchcl$symb"]/@value').get('').strip()
        searchcSYMBOL_US = response.xpath('//input[@name="ctl00$searchcl$SYMBOL_US"]/@value').get('').strip()
        contentcompany = response.xpath('//input[@name="ctl00$content$company"]/@value').get('').strip()
        contentcusip = response.xpath('//input[@name="ctl00$content$cusip"]/@value').get('').strip()

        payload={
            "__VIEWSTATE":view_state,
            "__VIEWSTATEGENERATOR":view_state_generator,
            "__EVENTVALIDATION":event_validation,
            "ctl00$inpt_txtSearch":inpt_txtSearch,
            "ctl00$searchcl$symb":earchclsymb,
            "ctl00$searchcl$SYMBOL_US":searchcSYMBOL_US,
            "ctl00$content$company":contentcompany,
            "ctl00$content$cusip":contentcusip,
            "ctl00$content$symb: ":"",
            "ctl00$content$country_id": "0",
            "ctl00$content$exc_cde": "0",
            "ctl00$content$dtf":'',
            "ctl00$content$dtt":'',
            "ctl00$content$announcementGroup1": "announcement_all",
            "ctl00$content$DistGroup1": "sponsored_all",
            "ctl00$content$announcement_for": "0",
            "ctl00$content$sort": "company_name",
            "ctl00$content$output": "EXCEL",
            "ctl00$content$search": "Search"         
        }
        url = 'https://depositaryreceipts.citi.com/adr/notices/corpActions.aspx?pageId=8&subpageid=6'
        yield scrapy.FormRequest(url,callback=self.parse_details_callback,formdata=payload,headers=self.headers)

    def parse_details_callback(self,response):
        if response.status == 200:
            df=pd.read_html(response.text)[0]
            final_df=df.fillna('')
            total_items = len(final_df)
            self.crawler.stats.set_value('no_record_count',self.no_record_count)
            self.crawler.stats.set_value('total_record_count',total_items)
            for index,row in final_df.iterrows():
                item=CitiCorporateItem()
                item['company'] = row['Company'].strip()
                date_of_notice=row['Date of Notice'].strip()
                item['date_of_notice']=self.datetime_format(date_of_notice)
                item['ticker']=row['Ticker'].strip()
                item['cusip']=row['CUSIP'].replace("'", "").strip()
                item['ratio_ord_dr']=row['Ratio (ORD:DR)'].replace("'", "").strip()
                item['type']=row['Type'].strip()
                item['country']=row['Country'].strip()
                item['exchange']=row['Exchange'].strip()
                item['corporate_action_type']=row['Corporate Action Type'].strip()
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