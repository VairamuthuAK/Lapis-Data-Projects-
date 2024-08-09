from common.items import CitiDistributionItem
from parsel import Selector
from datetime import datetime
import hashlib
import scrapy
import html
import os


class AdrCitiDsfDistributionsSpider(scrapy.Spider):
    name = "adrciti_dsfdistributions"

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
        'Referer': 'https://depositaryreceipts.citi.com/adr/guides/dsf.aspx?pageId=8&subpageid=190',
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
        url = 'https://depositaryreceipts.citi.com/adr/guides/dsf.aspx?pageId=8&subpageid=190'
        yield scrapy.Request(url,callback=self.parse,dont_filter =True) 

    def datetime_format(self,timedata):
        if timedata:
        # List of possible date formats
            formats = ["%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(timedata, fmt)
                    return date_obj.strftime("%Y%m%d")
                except ValueError:
                    continue
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
        ctl00contentactiveGroup=response.xpath('//input[@name="ctl00$content$activeGroup"]/@value').get('')
        serech=response.xpath('//input[@name="ctl00$content$search"]/@value').get('')

        payload={
            "__EVENTTARGET":"", 
            "__EVENTARGUMENT": "",
            "__VIEWSTATE":view_state, 
            "__VIEWSTATEGENERATOR":view_state_generator,
            "__EVENTVALIDATION": event_validation,
            "ctl00$searchcl$symb": earchclsymb,
            "ctl00$searchcl$SYMBOL_US":"", 
            "ctl00$content$activeGroup": ctl00contentactiveGroup,
            "ctl00$content$company": "",
            "ctl00$content$cusip": "",
            "ctl00$content$symb": "",
            "ctl00$content$country_id": "0",
            "ctl00$content$exc_cde": "0",
            "ctl00$content$dtf": "",
            "ctl00$content$dtt": "",
            "ctl00$content$adtf": "",
            "ctl00$content$adtt": "",
            "ctl00$content$sort": "company",
            "ctl00$content$output": "EXCEL",
            "ctl00$content$search": "Search",
        }
        url = 'https://depositaryreceipts.citi.com/adr/guides/dsf.aspx?pageId=8&subpageid=190'
        yield scrapy.FormRequest(url,callback=self.parse_details_callback,formdata=payload,headers=self.headers)

    def parse_details_callback(self,response):
        if response.status == 200:
            response=Selector(html.unescape(response.text.replace('<asp:','')))
            total_items = len(response.xpath('(//table[@id="dsftbl"])[1]//tr[not(position()=1)]').getall())
            self.crawler.stats.set_value('no_record_count',self.no_record_count)
            self.crawler.stats.set_value('total_record_count',total_items)
            for i in response.xpath('(//table[@id="dsftbl"])[1]//tr[not(position()=1)]'):
                item=CitiDistributionItem()
                item['company'] = i.xpath('./td[1]/text()').get('').replace(' \r\n','').strip()
                date_of_notice = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[2]//text()').getall()]).strip()
                item['date_of_notice'] =self.datetime_format(date_of_notice)
                item['ticker']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[3]//text()').getall()]).strip()
                item['cusip']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[4]//text()').getall()]).strip().replace("'", "")
                item['ratio_ord_dr']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[5]//text()').getall()]).strip().replace("'", "")
                item['type']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[6]//text()').getall()]).strip()
                item['country']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[7]//text()').getall()]).strip()
                item['exchange']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[8]//text()').getall()]).strip()
                record_date = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[9]//text()').getall()]).strip()
                item['record_date']=self.datetime_format(record_date)
                item['dsf_fee']  = ' '.join([data.replace(' \r\n','').strip() for data in i.xpath('./td[10]//text()').getall()]).strip()
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