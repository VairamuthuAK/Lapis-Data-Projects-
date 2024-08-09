# useful for handling different item types with a single interface
import pandas as pd
from datetime import datetime,timedelta
import os
import re
import scrapy
import logging
import time
import boto3
import io
import tempfile
import scrapy.signals
from utils import slack_spider_notofication,slack_spider_status


logger = logging.getLogger(__name__)


class AdrCitiPipeline: 
    def __init__(self, stats, crawler):
        current_day = datetime.now().weekday()
        self.historical_new_data_dump = []
        self.s3_client = boto3.client(
            service_name='s3',
        )
        if current_day == 6:
            self.target_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            self.target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.destination_date = datetime.now().strftime("%Y-%m-%d")
        self.spider_directory = 'citi'
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        logger.info(f'>----- Crawler Going to Start -----<')
        pipeline = cls(crawler.stats, crawler)
        crawler.signals.connect(pipeline.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=scrapy.signals.spider_closed)
        logger.info('>----- Going to return Pipeline -----<')
        return pipeline
    
    def spider_opened(self, spider):
        self.start_time = time.time()
        logger.info(f'Spider Going to Start -----> {spider.name}')
        hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.target_date}/{spider.name}.txt'
        hash_response = self.s3_client.get_object(Bucket=os.getenv('OUTPUT_BUCKET'), Key=hash_file_path)
        file_content = hash_response['Body'].read().decode('utf-8')
        hash_dump = re.split(r'\s+',file_content)
        self.hash_dumps = [element for element in hash_dump if element]
        message = slack_spider_notofication(spider.name, 'Started')
        if message:
            logger.info('Sending message in Slack Success !!!')
        else:
            logger.info('Sending message in Slack Failed !!!')

    def process_item(self, item, spider):
        logger.info('*** Processing Item ***')
        hash_name = item.get('hash')
        if spider.name != 'adrciti_twse':
            if hash_name in self.hash_dumps:
                logger.info(f'Hash in the previous dump -----> {hash_name}')
            else:
                logger.info(f'New Hash Detected ----> {hash_name}')
                self.historical_new_data_dump.append(dict(item))
                self.hash_dumps.append(hash_name)
        else:
            self.historical_new_data_dump.append(dict(item))
            self.hash_dumps.append(hash_name)
        return item
    
    def spider_closed(self, spider):
        parquet_dump_s3_path = f'output/historical/{self.spider_directory}/{self.target_date}/{spider.name}.parquet'
        parquet_upload_path = f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet'
        hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt'
        cosolidated_historical_path = f'output/consolidated_historical_file/{self.spider_directory}/{spider.name}.parquet'
        response = self.s3_client.get_object(Bucket=os.getenv('OUTPUT_BUCKET'), Key=parquet_dump_s3_path)
        parquet_data = response['Body'].read()
        parquet_file = io.BytesIO(parquet_data)
        existing_df = pd.read_parquet(parquet_file,engine='fastparquet')
        parquet_file.seek(0)
        new_record_count = len(self.historical_new_data_dump)
        if self.historical_new_data_dump:
            logger.info('Changes Detected!!!')
            new_df = pd.DataFrame(self.historical_new_data_dump,dtype=str)
            combined_pacquet_df = pd.concat([existing_df, new_df], ignore_index=True)
            final_df = combined_pacquet_df.drop('hash',axis=1)
            historical_data_count = len(combined_pacquet_df)
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
                tmp_paq_path = tmp_file.name
                final_df.to_parquet(tmp_paq_path, engine='fastparquet',compression='gzip')
                tmp_file.flush()
                tmp_file.seek(0)
            response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=parquet_upload_path,Body=open(tmp_paq_path,'rb'))
            consolidated_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=cosolidated_historical_path,Body=open(tmp_paq_path, 'rb'))
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
            historical_data_count = len(existing_df)
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
                tmp_paq_path = tmp_file.name
                existing_df.to_parquet(tmp_paq_path, engine='fastparquet',compression='gzip')
                tmp_file.flush()
                tmp_file.seek(0)
            response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=parquet_upload_path,Body=open(tmp_paq_path,'rb'))
            consolidated_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=cosolidated_historical_path,Body=open(tmp_paq_path, 'rb'))
            hash_dump = [element + '\n' for element in self.hash_dumps]
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
                temp_file.writelines(hash_dump)
                temp_file_path = temp_file.name
                temp_file.flush()
                temp_file.seek(0)
            txt_response = self.s3_client.put_object(Bucket=os.getenv('OUTPUT_BUCKET'),Key=hash_file_path,Body=open(temp_file_path, 'rb'))
            os.remove(temp_file_path)
            self.s3_client.close()
        item_scraped_count = self.stats.get_value('item_scraped_count',0)
        no_record_count = self.stats.get_value('no_record_count',0)
        duplicate_record_count = self.stats.get_value('dupefilter/filtered',0)
        total_record_count = self.stats.get_value('total_record_count',0)
        error_status = self.stats.get_value('log_count/ERROR')
        finish_status = self.stats.get_value('finish_reason')
        spider_notification = slack_spider_status(spider.name, item_scraped_count, new_record_count, no_record_count, duplicate_record_count, historical_data_count, total_record_count, error_status, finish_status)
        if spider_notification:
            logger.info('Sending spider status in Slack Success !!!')
        else:
            logger.info('Sending spider status in Slack Failed !!!')
        logger.info(f'Spider Closed -----> {spider.name}')
        message = slack_spider_notofication(spider.name, 'Completed')
        if message:
            logger.info('Sending message in Slack Success !!!')
        else:
            logger.info('Sending message in Slack Failed !!!')