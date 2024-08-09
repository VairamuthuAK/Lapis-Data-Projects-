from common.items import CitiUniverseItem
from datetime import datetime
import pandas as pd
import hashlib
import scrapy
import os


class AdrCitiUniverseSpider(scrapy.Spider):
    name = "adrciti_universe"

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

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://depositaryreceipts.citi.com',
        'Pragma': 'no-cache',
        'Referer': 'https://depositaryreceipts.citi.com/adr/guides/uig.aspx?pageId=8&subpageid=34',
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
        url = 'https://depositaryreceipts.citi.com/adr/guides/uig.aspx?pageId=8&subpageid=34'
        yield scrapy.Request(url,callback=self.parse,dont_filter =True) 

    def datetime_format(self,timedata):
        if timedata:
            formats = ["%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(timedata, fmt)
                    return date_obj.strftime("%Y%m%d")
                except ValueError:
                    continue
            return ''
        else:
            return ''

    def parse(self, response):
        view_state = response.xpath('//input[@name="__VIEWSTATE"]/@value').get('').strip()
        view_state_generator = response.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').get('').strip()
        event_validation = response.xpath('//input[@name="__EVENTVALIDATION"]/@value').get('').strip()
        inpt_txtSearch = response.xpath('//input[@name="ctl00$inpt_txtSearch"]/@value').get('').strip()
        earchclsymb = response.xpath('//input[@name="ctl00$searchcl$symb"]/@value').get('').strip()
        contentactiveGroup = response.xpath('//input[@name="ctl00$content$activeGroup1"]/@value').get('').strip()
        ctl00contentSponsoredGroup1=response.xpath('(//input[@name="ctl00$content$SponsoredGroup1"])[3]/@value').get('')

        payload={
            "__EVENTTARGET":"",
            "__EVENTARGUMENT":"", 
            "__VIEWSTATE":view_state, 
            "__VIEWSTATEGENERATOR":view_state_generator,
            "__EVENTVALIDATION":event_validation,
            "ctl00$inpt_txtSearch":inpt_txtSearch,
            "ctl00$searchcl$symb":earchclsymb,
            "ctl00$searchcl$SYMBOL_US":"",
            "ctl00$content$company":"",
            "ctl00$content$cusip":"", 
            "ctl00$content$SponsoredGroup1":ctl00contentSponsoredGroup1,
            "ctl00$content$activeGroup1":contentactiveGroup,
            "ctl00$content$dtf":"", 
            "ctl00$content$dtt":"", 
            "ctl00$content$isin":"", 
            "ctl00$content$underisin":"",
            "ctl00$content$undersedol":"", 
            "ctl00$content$undersymb":"", 
            "ctl00$content$comments":"", 
            "ctl00$content$Hstatus":"", 
            "ctl00$content$excelBtn.x":"6",
            "ctl00$content$excelBtn.y":"8",}
        
        url = 'https://depositaryreceipts.citi.com/adr/guides/uig.aspx?pageId=8&subpageid=34'
        yield scrapy.FormRequest(url,callback=self.parse_details_callback,formdata=payload,headers=self.headers)


    def parse_details_callback(self,response):
        if response.status == 200:
            df=pd.read_html(response.text)[0]
            final_df = df.fillna('')
            total_items = len(final_df)
            self.crawler.stats.set_value('no_record_count',self.no_record_count)
            self.crawler.stats.set_value('total_record_count',total_items)
            for index,row in final_df.iterrows():
                item = CitiUniverseItem()
                item['issuer']=row['Issuer']
                item['active']=row['Active']
                item['country']=row['Country']
                item['region']=row['Region']
                item['sp_un']=row['Sp/Un']
                item['depositary']=row['Depositary'] 
                item['custodian1_or_register']=row['Custodian1/Registrar']
                item['custodian2']=row['Custodian2']
                item['custodian3']=row['Custodian3']
                item['structure']=row['Structure']
                item['private']=row['Private']
                item['upgrade']=row['Upgrade']
                item['successor']=row['Successor']
                item['single_listed']=row['Single-listed']
                item['effective']=self.datetime_format(row['Effective'])
                item['ratio_ord_adr']=row['Ratio (ORD:ADR)'].replace("'", "")
                item['exchange']=row['Exchange']
                item['ticker']=row['Ticker']
                item['cusip']=row['CUSIP'].replace("'", "")
                item['dr_share_isin']=row['DR Share ISIN']
                item['ordinary_isin']=row['Ordinary ISIN']
                item['ordinary_sedol']=row['Ordinary Sedol']
                item['ordinary_ticker']=row['Ordinary ticker']
                item['gics_industry']=row['GICS Industry']
                item['product_milestones']=row['Product Milestones']
                item['comments']=row['Comments']
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