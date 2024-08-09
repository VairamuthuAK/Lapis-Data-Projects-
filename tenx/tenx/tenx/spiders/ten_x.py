# import scrapy
# from scrapy import signals
# from playwright.sync_api import sync_playwright
# import time
# import json
# from parsel import Selector 
# import json
# import hashlib
# import re 
# from tenx.items import TenxItem
# import asyncio

# from itemadapter import ItemAdapter
# import pandas as pd
# from datetime import datetime, timedelta
# import os
# import scrapy
# import logging
# import time
# import boto3
# import io
# import tempfile
# import scrapy.signals
# from dotenv import load_dotenv

# logger = logging.getLogger(__name__)

# load_dotenv()

# def format_currency(value):
#     if value is None:
#         return value
#     try:
#         if value >= 1_000_000_000:
#             formatted_value = f"${value / 1_000_000_000:.1f}B"
#         elif value >= 1_000_000:
#             formatted_value = f"${value / 1_000_000:.1f}M"
#         elif value >= 1_000:
#             formatted_value = f"${value / 1_000:.1f}k"
#         else:
#             formatted_value = f"${value}"
#         return formatted_value
#     except (TypeError, ValueError):
#         return value
    
# def format_as_percentage(value):
#     if value is None:
#         return value
#     try:
#         # Try to convert the value to a float and format as a percentage
#         float_value = float(value)
#         return f"{float_value}%"
#     except ValueError:
#         # If conversion fails, return the original value
#         return value
    
    
# def format_number(value):
#     if value is None:
#         return value
#     try:
#         # Try to convert the value to a float
#         float_value = float(value)
        
#         # Check if the float value is an integer
#         if float_value.is_integer():
#             float_value = int(float_value)
        
#         # Format based on the value
#         if float_value >= 1_000_000_000:
#             return f"{float_value / 1_000_000_000:.1f}B"
#         elif float_value >= 1_000_000:
#             return f"{float_value / 1_000_000:.1f}M"
#         elif float_value >= 1_000:
#             return f"{float_value / 1_000:.1f}k"
#         else:
#             return float_value if isinstance(float_value, float) else int(float_value)
#     except ValueError:
#         # If conversion fails, return the original value
#         return value
    

# def convert_to_percentage(value):
#     if value is None:
#         return value
#     try:
#         # Try to convert the value to a float
#         float_value = float(value)
        
#         # Convert to percentage and format to one decimal place
#         percentage_value = float_value * 100
#         formatted_percentage = f"{percentage_value:.1f}%"
        
#         return formatted_percentage
#     except ValueError:
#         # If conversion fails, return the original value
#         return value
    
# def remove_key(data):
#     if str(data).strip() == "-":
#         return None
#     else:
#         return data
    
# class TenXSpider(scrapy.Spider):
#     name = 'tenx'

#     current_day = datetime.now().weekday()
#     historical_new_data_dump = []
#     daily_data_dump = []
#     s3_client = boto3.client('s3')
#     target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
#     destination_date = datetime.now().strftime("%Y-%m-%d")
#     spider_directory = 'tenx'
#     hash_dumps = []
    
#     custom_settings = {
#             # 'ITEM_PIPELINES': {
#             #     'tenx.pipeline.TenxPipeline': 300,
#             # },
#             'FEED_EXPORT_ENCODING': 'utf-8',
#             # 'LOG_FILE': log_file,
#             'LOG_LEVEL': 'INFO',
#             # 'FEEDS': {f"s3://{os.getenv('OUTPUT_BUCKET')}/output/daily_collections/tenx/{current_date}/{name}.json": {"format": "json"}},
#         }

#     decode_headers={}
    
#     @classmethod
#     def from_crawler(cls, crawler, *args, **kwargs):
#         spider = super(TenXSpider, cls).from_crawler(crawler, *args, **kwargs)
#         crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
#         crawler.signals.connect(spider.spider_closed, signals.spider_closed)
#         return spider
    
#     def spider_opened(self):
#         self.login_headers={}
#         playwright = sync_playwright().start()
#         browser = playwright.chromium.launch(headless=True,args=["--start-maximized"])
#         self.context = browser.new_context(java_script_enabled=True)
#         self.page = self.context.new_page()
#         self.page.goto('https://www.ten-x.com/',wait_until='load',timeout=0)
#         self.page.locator('//a[@data-elm-id="POPUP_MENU_LOGIN"]').click()
#         asyncio.sleep(5)
#         fill_box = self.page.locator('//input[@name="email"]')
#         fill_box.fill("bayawe3515@morxin.com")
#         self.page.locator('//button[@type="submit"]').click()
#         asyncio.sleep(5)
#         fill_box = self.page.locator("//input[@id = 'password']")
#         fill_box.fill("Sadfgqwe")
#         with self.page.expect_request("https://www.ten-x.com/") as first:
#             self.page.locator('//button[@id="loginButton"]').click()
#         first_request = first.value
#         self.login_headers=first_request.headers
#         self.log(f'{self.login_headers}')
#         self.start_time = time.time()
#         logger.info(f'Spider Going to Start -----> {self.name}')

#     def process_item(self, item,spider):
#         breakpoint()
#         logger.info('*** Processing Item ***')
#         hash_name = item.get('hash')
#         self.historical_new_data_dump.append(dict(item))

#         self.hash_dumps.append(hash_name)

#         return item
    
#     def spider_closed(self, spider):
#         try:
#             self.page.close()
#         except:
#             pass
#         parquet_upload_path = f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet'
#         hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt'
#         # breakpoint()
#         new_df = pd.DataFrame(self.historical_new_data_dump, dtype=str)
#         final_df = new_df.drop('hash', axis=1)
        
#         # Save DataFrame to Parquet
#         with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
#             tmp_paq_path = tmp_file.name
#             final_df.to_parquet(tmp_paq_path, engine='fastparquet', compression='gzip')
#             tmp_file.flush()
#             tmp_file.seek(0)
        
#         # Upload Parquet to S3
#         response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'), Key=parquet_upload_path, Body=open(tmp_paq_path, 'rb'))
#         os.remove(tmp_paq_path)  # Clean up the temporary file
        
#         # Save hash to text file
#         hash_dump = [element + '\n' for element in self.hash_dumps]
#         with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
#             temp_file.writelines(hash_dump)
#             temp_file_path = temp_file.name
#             temp_file.flush()
#             temp_file.seek(0)
        
#         # Upload hash file to S3
#         txt_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'), Key=hash_file_path, Body=open(temp_file_path, 'rb'))
#         os.remove(temp_file_path)  # Clean up the temporary file
        
#         self.s3_client.close()
#         logger.info(f'Spider Closed -----> {spider.name}')


#     start_urls = ['https://www.ten-x.com/']
#     # start_url=['https://www.ten-x.com/search/all_limit/']

#     def parse(self, response):
#         us_states = [
#                 "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
#                 "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
#                 "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
#                 "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
#                 "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
#                 "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
#                 "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
#                 "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
#                 "Washington", "West Virginia", "Wisconsin", "Wyoming"
#             ]
#         for state in us_states:
#             url="https://www.ten-x.com/search/cu/api/86a5qs/api/v1/listing/search?page=0&size=200"
#             payload = {
#             "rl": 500,
#             "sort": 0,
#             "criteria": {
#                 "ccs": 1,
#                 "bldgAreaUom": 1,
#                 "landAreaUom": 3,
#                 "currency": 1,
#                 "sale": {
#                 "auction": {
#                     "auctionListingTypes": 31
#                 },
#                 "conditions": "256",
#                 "auctionStatuses": 3
#                 },
#                 "kq": state
#             }
#             }
#             headers = {
#             'accept': 'application/json',
#             'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#             'cache-control': 'no-cache',
#             'content-type': 'application/json',
#             'origin': 'https://www.ten-x.com',
#             'pragma': 'no-cache',
#             'priority': 'u=1, i',
#             'referer': f'https://www.ten-x.com/search/{state}_qs/',
#             # 'referer' : 'https://www.ten-x.com/search/all_limit/',

#             }
#             headers.update(self.login_headers)
#             yield scrapy.Request(url,method="POST",headers=headers,body=json.dumps(payload),callback=self.parse_detail)

#     def parse_detail(self,response):
#         for block in response.json()['data']:
#             url=block['ldpUrl']
#             self.decode_headers = { y.decode('ascii'): response.headers.get(y).decode('ascii') for y in response.headers.keys()}
#             self.decode_headers.pop('Set-Cookie', None)
#             self.decode_headers.update(self.login_headers)
#             self.decode_headers['accept']= 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
#             self.decode_headers['accept-language']= 'en-GB,en-US;q=0.9,en;q=0.8'
#             self.log(self.decode_headers)
#             yield scrapy.Request(url,callback=self.parse_details,headers=self.decode_headers)
    
#     async def parse_details(self,response):
#         try:
#             # property_id=response.url.split('/')[-2]
#             # link=f"https://www.ten-x.com/listing/cu/api/86a5qs/api/v1/listing/{property_id}/analytics"
#             # costar_data=await self.request_process(link,{})
#             # # with open(f'{property_id}.html','w') as f:f.write(costar_analytics.text)
#             # response=await self.request_process(response.url,{})

#             # costar_data=json.loads(costar_data.text)
#             # item={}
#             item=TenxItem()
#             item['source_url'] = response.url
#             item['name'] = response.xpath('//h1[@data-elm-id="prop_name"]//text()').get()
#             # breakpoint()
#             # item['asset_type'] = response.xpath('//span[@data-elm-id="asset_type_content"]//text()').get()
#             # primary_property_type_1=response.xpath('//span[@data-elm-id="condo_primary_type_content"]//text()').get()
#             # primary_property_type_2=response.xpath('//span[@data-elm-id="primary_type_content"]//text()').get()
#             # if primary_property_type_1:
#             #     item['primary_property_type']=primary_property_type_1
#             # elif primary_property_type_2:
#             #     item['primary_property_type']=primary_property_type_2
#             # else:
#             #     item['primary_property_type']=None 
        
#             # item['primary_sub_type']=response.xpath('//span[@data-elm-id="primary_sub_type_content"]//text()').get()

#             # property_address=response.xpath('//span[@data-elm-id="prop_address"]//text()').get()
#             # if property_address:
#             #     item['property_address']=property_address
#             # else:
#             #     property_info={}                
#             #     property_address_1 = response.xpath('//div[@class="ant-row investment-oportunity-address_styles_PR3J"]')
#             #     for index, property in enumerate(property_address_1,1):
#             #         property_info[f'property_address_{index}'] =property.xpath('.//div[1]/text()').get()
#             #         property_info[f'property_type_{index}'] =property.xpath('.//div[2]/text()').get()
#             #         property_info[f'property_size_{index}_(sq.ft.)'] =property.xpath('.//div[3]/text()').get().replace('(Sq. Ft.)','')
#             #     item['property_info']=property_info

#             # item['offering_size_sq_ft']=response.xpath('//span[@data-elm-id="offering_size_content"]//text()').get()
#             # item['starting_bid']=response.xpath('//span[@data-elm-id="mobile_start_bid_amount"]//text()').get()
#             # # item['online_auction']=response.xpath('//span[@data-elm-id="bidding-box-auction-dates-value"]//text()').get()
#             # item['event_item']=response.xpath('//span[@data-elm-id="event-item"]//text()').get()
#             # item['units']=response.xpath('//span[@data-elm-id="units_content"]//text()').get()
#             # item['building_size_sq_ft']=response.xpath('//span[@data-elm-id="building_size_content"]//text()').get()
#             # year_built=response.xpath('//span[@data-elm-id="year_built_content"]//text()').get()
#             # if year_built:
#             #     item['year_built']=year_built
#             # else:
#             #     item['year_built']=response.xpath('//span[@data-elm-id="mobile_year_built"]//text()').get()
#             # item['occupancy']=response.xpath('//span[@data-elm-id="occupancy_content"]//text()').get()
#             # item['type_of_ownership']=response.xpath('//span[@data-elm-id="type_of_ownership"]//text()').get()
#             # item['lot_size_acres']=response.xpath('//span[@data-elm-id="lot_size_content"]//text()').get()
#             # item['floors']=response.xpath('//span[@data-elm-id="mobile_floors"]//text()').get()
#             # item['assessor_parcel_number']=response.xpath('//span[@data-elm-id="mobile_apn"]//text()').get()
#             # property_id=response.xpath('//span[@data-elm-id="property_id"]//text()').get()
#             # if property_id:
#             #     item['property_id']=property_id
#             # else:
#             #     item['property_id']=response.xpath('//span[@data-elm-id="property-id"]//text()').get()
#             # item['building_class']=response.xpath('//span[@data-elm-id="mobile_building_class"]//text()').get()
#             # item['starting_bid']=response.xpath('//span[@data-elm-id="mobile_start_bid_amount"]//text()').get()
#             # item['year_renovated']=response.xpath('//span[@data-elm-id="mobile_year_renovated"]//text()').get()
#             # item['zoning_designation']=response.xpath('//span[@data-elm-id="mobile_zoning_designation"]//text()').get()
#             # item['parking_ratio']=response.xpath('//span[@data-elm-id="mobile_parking_ratio"]//text()').get()
#             # item['parking_count']=response.xpath('//span[@data-elm-id="mobile_parking_count"]//text()').get()
#             # item['common_amenities']=response.xpath('//span[@data-elm-id="mobile_common_amenities"]//text()').get()
#             # item['unit_amenities']=response.xpath('//span[@data-elm-id="mobile_unit_amenities"]//text()').get()
#             # item['rooms']=response.xpath('//span[@data-elm-id="mobile_rooms"]//text()').get()
#             # item['building_coverage_ratio']=response.xpath('//span[@data-elm-id="mobile_coverage_ratio"]//text()').get()
#             # item['description']=response.xpath('//div[@class="detailed-desc-container"]//p/text()').get()
#             # item['property_information']=''.join(response.xpath('//h4[contains(text(), "Property Information")]/following-sibling::div[@data-elm-id="property-info-highlights"]/div/text()').getall()).strip()
#             # all_images=[]
#             # if re.search(r'media_uri\"\:\"(.*?)\s*\"\}',response.text):
#             #     img = re.findall(r'media_uri\"\:\"(.*?)\s*\"\}',response.text)
#             #     for images in img:
#             #         if len(images) > 50:
#             #             all_images.append(images)
#             # item['images']= all_images

#             # key_metrics={}
#             # datas=costar_data.get('data','').get('marketOverview','').get('salesVolume','').get('header','')
#             # if len(datas)>0:
#             #     for data in datas:
#             #         header_1 = data.get('displayName','')
#             #         key_metrics[header_1] = format_currency(data.get('value',''))
#             # datas2=costar_data.get('data','').get('marketOverview','').get('salesVolume','').get('rows','')
            
#             # if len(datas2)>0:
#             #     for dat in datas2:
#             #         header_1 = dat.get('displayName','')
#             #         value_type = dat.get('valueType','')
#             #         sub_datas=dat.get('columns','')
#             #         if len(sub_datas)>0:
#             #             for sub_dt in sub_datas:
#             #                 sub_header1 = sub_dt.get('displayName','')
#             #                 if value_type =='CURRENCY':
                                
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics[f'{header_1}_{sub_header1}'] = format_currency(sub_dt.get('value',''))
#             #                 elif value_type == 'PERCENTAGE':
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics[f'{header_1}_{sub_header1}'] = convert_to_percentage(sub_dt.get('value',''))
                            
#             #                 elif value_type == 'NUMBER':
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics[f'{header_1}_{sub_header1}'] = format_number(sub_dt.get('value',''))
#             #                 else:
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics[f'{header_1}_{sub_header1}'] = sub_dt.get('value','')
#             # item['key_metrics'] = key_metrics
                
#             # datas3=costar_data.get('data','').get('marketOverview','').get('salesPrice','').get('header','')
#             # # item={}
#             # key_metrics_1={}
#             # if len(datas3)>0:
#             #     for idx, data_3 in enumerate(datas3):
#             #         header_1 = data_3.get('displayName','')
#             #         if idx==0:
                        
#             #             key_metrics_1[header_1] = convert_to_percentage(data_3.get('value',''))
#             #         else:
#             #             key_metrics_1[header_1] = convert_to_percentage(data_3.get('value',''))
            
#             # datas4=costar_data.get('data','').get('marketOverview','').get('salesPrice','').get('rows','')
#             # if len(datas4)>0:
#             #     for dat4 in datas4:
#             #         header_1 = dat4.get('displayName','')
#             #         value_type = dat4.get('valueType','')
#             #         sub_datas=dat4.get('columns','')
#             #         if len(sub_datas)>0:
#             #             for sub_dt in sub_datas:
#             #                 sub_header1 = sub_dt.get('displayName','')
#             #                 if value_type =='CURRENCY':
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics_1[f'{header_1}_{sub_header1}'] = format_currency(sub_dt.get('value',''))
#             #                 elif value_type == 'PERCENTAGE':
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics_1[f'{header_1}_{sub_header1}'] = format_as_percentage(sub_dt.get('value',''))
                            
#             #                 elif value_type == 'NUMBER':
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics_1[f'{header_1}_{sub_header1}'] = format_number(sub_dt.get('value',''))
#             #                 else:
#             #                     sub_header_value = sub_dt.get(sub_header1)
#             #                     key_metrics_1[f'{header_1}_{sub_header1}'] = sub_dt.get('value','')
#             # item['key_metrics_1']=key_metrics_1
#             all_values = [str(item[key]) for key in dict(item)]
#             hash_obj = hashlib.md5(('_'.join(all_values)).encode('utf-8'))
#             item['hash'] = hash_obj.hexdigest()
#             yield item
#         except:
#             self.log('=====================error====================')

        

#     async def request_process(self,url,payload):
#         if payload=={}:
#             request=scrapy.Request(url,headers=self.decode_headers)
#         else:
#             request=scrapy.Request(url,method='POST',headers=self.decode_headers,body=payload)
#         response = await self.crawler.engine.download(request)
#         return response

