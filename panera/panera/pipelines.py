
#-------------------------------------> INITIAL DUMP USING THIS PIPELINE <-------------------------------------------------------------------#

import pandas as pd
from datetime import datetime,timedelta
import os
import scrapy
import logging
import time
import boto3
import io
import tempfile
import scrapy.signals
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Panera2Pipeline:
    def __init__(self):
        current_day = datetime.now().weekday()
        self.historical_new_data_dump = []
        self.daily_data_dump = []
        session = boto3.Session(profile_name='account_production')
        self.s3_client=session.client('s3')

        self.target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.destination_date = datetime.now().strftime("%Y-%m-%d")
        self.spider_directory = 'panera'
        self.hash_dumps = []
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=scrapy.signals.spider_closed)
        return pipeline
    def spider_opened(self, spider):
        self.start_time = time.time()
        logger.info(f'Spider Going to Start -----> {spider.name}')


    def process_item(self, item, spider):
        logger.info('*** Processing Item ***')
        hash_name = item.get('hash')
        self.historical_new_data_dump.append(dict(item))
        self.hash_dumps.append(hash_name)
        return item
    
    def spider_closed(self, spider):
        parquet_upload_path = f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet'
        hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt'
        # json_upload_path = f'output/daily_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.json'
        cosolidated_historical_path = f'output/consolidated_historical_file/{self.spider_directory}/{spider.name}.parquet'
        new_df = pd.DataFrame(self.historical_new_data_dump,dtype=str)
        final_df = new_df.drop('hash',axis=1)
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
            tmp_paq_path = tmp_file.name
            final_df.to_parquet(tmp_paq_path, engine='fastparquet',compression='gzip')
            tmp_file.flush()
            tmp_file.seek(0)
        response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=parquet_upload_path,Body=open(tmp_paq_path,'rb'))
        # consolidated_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=cosolidated_historical_path,Body=open(temp_paq_path, 'rb'))
        consolidated_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=cosolidated_historical_path,Body=open(tmp_paq_path,'rb'))
        hash_dump = [element + '\n' for element in self.hash_dumps]
        
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
            temp_file.writelines(hash_dump)
            temp_file_path = temp_file.name
            temp_file.flush()
            temp_file.seek(0)
        txt_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=hash_file_path,Body=open(temp_file_path, 'rb'))
        os.remove(temp_file_path)
        self.s3_client.close()
        logger.info(f'Spider Closed -----> {spider.name}')


#===========================================================================================================================================================================
 #-----------------------------------------------> COMPRESSION USING THIS PIPELINE <-------------------------------------------------------#


import pandas as pd
from datetime import datetime,timedelta
import os
import scrapy
import logging
import time
import boto3
import json
import io
import re
import tempfile
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
class Panera2Pipeline:
    def __init__(self,spider_name):
        current_day = datetime.now().weekday()
        self.historical_new_data_dump = []
        self.daily_data_dump = []
        self.hash_dumps=[]
        session = boto3.Session()
        # # session = boto3.Session()
        self.s3_client=session.client('s3')
        
        if spider_name =='panera_location':
            current_date = datetime.now()
            self.target_date = current_date.replace(day=1).strftime("%Y-%m-%d")  
        elif spider_name =='panera_product':
            self.target_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d") 
            self.target_date='2024-07-11'
        self.target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if current_day == 0:  
            self.target_date = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")  
        elif current_day == 3:
            self.target_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")  
        self.destination_date = datetime.now().strftime("%Y-%m-%d")
        self.spider_directory = 'panera'
    @classmethod
    def from_crawler(cls, crawler):
        spider_name = crawler.spider.name
        pipeline = cls(spider_name)
        crawler.signals.connect(pipeline.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=scrapy.signals.spider_closed)
        return pipeline
    
    def spider_opened(self, spider):
        self.start_time = time.time()
        logger.info(f'Spider Going to Start -----> {spider.name}')
        hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.target_date}/{spider.name}.txt'
        hash_response = self.s3_client.get_object(Bucket=os.getenv('OUTPUT_BUCKET'), Key=hash_file_path)
        file_content = hash_response['Body'].read().decode('utf-8')
        hash_dump = re.split(r'\s+',file_content)
        
        self.hash_dumps = [element for element in hash_dump if element]
    def process_item(self, item, spider):
        logger.info('*** Processing Item ***')
        hash_name = item.get('hash')
        if hash_name in self.hash_dumps:
            logger.info(f'Hash in the previous dump -----> {hash_name}')
        else:
            logger.info(f'New Hash Detected ----> {hash_name}')
            self.historical_new_data_dump.append(dict(item))
            self.hash_dumps.append(hash_name)
        self.daily_data_dump.append(dict(item))
        return item
    
    def spider_closed(self, spider):
        parquet_dump_s3_path = f'output/historical/{self.spider_directory}/{self.target_date}/{spider.name}.parquet'
        parquet_upload_path = f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet'
        json_upload_path = f'output/daily_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.json'
        hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt'
        cosolidated_historical_path = f'output/consolidated_historical_file/{self.spider_directory}/{spider.name}.parquet'
        
        response = self.s3_client.get_object(Bucket=os.getenv('OUTPUT_BUCKET'), Key=parquet_dump_s3_path)
        parquet_data = response['Body'].read()
        parquet_file = io.BytesIO(parquet_data)
        existing_df = pd.read_parquet(parquet_file,engine='fastparquet')
        parquet_file.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
            temp_file.write("[\n")
            for index, data in enumerate(self.daily_data_dump):
                json.dump(data, temp_file, ensure_ascii=False)
                if index < len(self.daily_data_dump) - 1:
                    temp_file.write(',\n')
            temp_file.write("\n]")
            temp_file_path = temp_file.name
            temp_file.flush()
            temp_file.seek(0)
        json_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=json_upload_path,Body=open(temp_file_path, 'rb'))
        if self.historical_new_data_dump:
            logger.info('Changes Detected!!!')
            new_df = pd.DataFrame(self.historical_new_data_dump,dtype=str)
            combined_pacquet_df = pd.concat([existing_df, new_df], ignore_index=True)
            final_df = combined_pacquet_df.drop('hash',axis=1)
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
                tmp_paq_path = tmp_file.name
                final_df.to_parquet(tmp_paq_path, engine='fastparquet')
                tmp_file.flush()
                tmp_file.seek(0)
            response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=parquet_upload_path,Body=open(tmp_paq_path,'rb'))
            consolidated_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=cosolidated_historical_path,Body=open(tmp_paq_path,'rb'))
    
            hash_dump = [element + '\n' for element in self.hash_dumps]
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
                temp_file.writelines(hash_dump)
                temp_file_path = temp_file.name
                temp_file.flush()
                temp_file.seek(0)
            txt_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=hash_file_path,Body=open(temp_file_path, 'rb'))
            os.remove(temp_file_path)
            self.s3_client.close()
        else:
            logger.info('No Changes Detected....')
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
                tmp_paq_path = tmp_file.name
                existing_df.to_parquet(tmp_paq_path, engine='fastparquet')
                tmp_file.flush()
                tmp_file.seek(0)
            response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=parquet_upload_path,Body=open(tmp_paq_path,'rb'))
            hash_dump = [element + '\n' for element in self.hash_dumps]
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
                temp_file.writelines(hash_dump)
                temp_file_path = temp_file.name
                temp_file.flush()
                temp_file.seek(0)
            txt_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=hash_file_path,Body=open(temp_file_path, 'rb'))
            os.remove(temp_file_path)
            self.s3_client.close()
        logger.info(f'Spider Closed -----> {spider.name}')


