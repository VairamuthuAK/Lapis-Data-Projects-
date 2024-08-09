# import pandas as pd
# from datetime import datetime, timedelta
# import os
# import json
# import scrapy
# import logging
# import time
# import io
# import tempfile
# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)

# class TenxPipeline:

#     def __init__(self):
#         current_day = datetime.now().weekday()
#         self.historical_new_data_dump = []
#         self.daily_data_dump = []
#         self.target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
#         self.destination_date = '2024-07-08'
#         self.spider_directory = 'tenx'
#         self.hash_dumps = []

#     @classmethod
#     def from_crawler(cls, crawler):
#         pipeline = cls()
#         crawler.signals.connect(pipeline.spider_opened, signal=scrapy.signals.spider_opened)
#         crawler.signals.connect(pipeline.spider_closed, signal=scrapy.signals.spider_closed)
#         return pipeline
    
#     def spider_opened(self, spider):
#         self.start_time = time.time()
#         logger.info(f'Spider Going to Start -----> {spider.name}')
#         hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.target_date}/{spider.name}.txt'
#         if os.path.exists(hash_file_path):
#             with open(hash_file_path, 'r') as f:
#                 self.hash_dumps = [line.strip() for line in f if line.strip()]
        
#     def process_item(self, item, spider):
#         logger.info('*** Processing Item ***')
        
#         hash_name = item.get('hash')
#         if hash_name in self.hash_dumps:
#             logger.info(f'Hash in the previous dump -----> {hash_name}')
#         else:
#             logger.info(f'New Hash Detected ----> {hash_name}')
#             self.historical_new_data_dump.append(dict(item))
#             self.hash_dumps.append(hash_name)
#         self.daily_data_dump.append(dict(item))
#         return item
    
#     def spider_closed(self, spider):
#         parquet_dump_local_path = f'output/historical/{self.spider_directory}/{self.target_date}/{spider.name}.parquet'
#         parquet_upload_path = f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet'
#         json_upload_path = f'output/daily_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.json'
#         hash_file_path = f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt'
#         consolidated_historical_path = f'output/consolidated_historical_file/{self.spider_directory}/{spider.name}.parquet'
#         if os.path.exists(parquet_dump_local_path):
#             existing_df = pd.read_parquet(parquet_dump_local_path, engine='fastparquet')
#         else:
#             existing_df = pd.DataFrame()

#         with open(json_upload_path, 'w') as f:
#             json.dump(self.daily_data_dump, f)

#         if self.historical_new_data_dump:
#             logger.info('Changes Detected!!!')
#             new_df = pd.DataFrame(self.historical_new_data_dump, dtype=str)
#             combined_parquet_df = pd.concat([existing_df, new_df], ignore_index=True)
#             final_df = combined_parquet_df.drop('hash', axis=1)
#             final_df.to_parquet(parquet_upload_path, engine='fastparquet')
#             final_df.to_parquet(consolidated_historical_path, engine='fastparquet')

#             with open(hash_file_path, 'w') as f:
#                 f.writelines([f"{hash}\n" for hash in self.hash_dumps])
#         else:
#             logger.info('No Changes Detected....')
#             existing_df.to_parquet(parquet_upload_path, engine='fastparquet')
#             existing_df.to_parquet(consolidated_historical_path, engine='fastparquet')

#             with open(hash_file_path, 'w') as f:
#                 f.writelines([f"{hash}\n" for hash in self.hash_dumps])

#         logger.info(f'Spider Closed -----> {spider.name}')
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import pandas as pd
from datetime import datetime, timedelta
import json
import scrapy
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TenxPipeline:
    def __init__(self):
        current_day = datetime.now().weekday()
        self.historical_new_data_dump = []
        self.daily_data_dump = []
        self.target_date = '2024-08-05' 
        self.destination_date = '2024-08-09'    
        self.spider_directory = 'tenx'
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
        try:
            hash_file_path = Path(f'output/hash_collections/{self.spider_directory}/{self.target_date}/{spider.name}.txt')
            if hash_file_path.exists():
                with hash_file_path.open('r') as f:
                    self.hash_dumps = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error while opening hash file: {e}")
        
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
        parquet_dump_local_path = Path(f'output/historical/{self.spider_directory}/{self.target_date}/{spider.name}.parquet')
        parquet_upload_path = Path(f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet')
        json_upload_path = Path(f'output/daily_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.json')
        hash_file_path = Path(f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt')
        consolidated_historical_path = Path(f'output/consolidated_historical_file/{self.spider_directory}/{spider.name}.parquet')

        try:
            # Ensure directories exist
            parquet_dump_local_path.parent.mkdir(parents=True, exist_ok=True)
            parquet_upload_path.parent.mkdir(parents=True, exist_ok=True)
            json_upload_path.parent.mkdir(parents=True, exist_ok=True)
            hash_file_path.parent.mkdir(parents=True, exist_ok=True)
            consolidated_historical_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing data
            existing_df = pd.read_parquet(parquet_dump_local_path, engine='fastparquet') if parquet_dump_local_path.exists() else pd.DataFrame()

            # Write daily data to JSON row-wise
            with json_upload_path.open('w') as f:
                for item in self.daily_data_dump:
                    json.dump(item, f)
                    f.write('\n')

            if self.historical_new_data_dump:
                logger.info('Changes Detected!!!')
                new_df = pd.DataFrame(self.historical_new_data_dump, dtype=str)
                combined_parquet_df = pd.concat([existing_df, new_df], ignore_index=True)
                final_df = combined_parquet_df.drop('hash', axis=1)
                final_df.to_parquet(parquet_upload_path, engine='fastparquet')
                final_df.to_parquet(consolidated_historical_path, engine='fastparquet')
            else:
                logger.info('No Changes Detected....')
                existing_df.to_parquet(parquet_upload_path, engine='fastparquet')
                existing_df.to_parquet(consolidated_historical_path, engine='fastparquet')

            # Write updated hash file
            with hash_file_path.open('w') as f:
                f.writelines([f"{hash}\n" for hash in self.hash_dumps])

        except Exception as e:
            logger.error(f"Error while processing: {e}")

        logger.info(f'Spider Closed -----> {spider.name}')




# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------------------------------

# import pandas as pd
# from datetime import datetime, timedelta
# import os
# import scrapy
# import logging
# import time
# import tempfile
# import shutil
# from pathlib import Path
# import json
# import scrapy.signals

# logger = logging.getLogger(__name__)

# class TenxPipeline:
#     def __init__(self):
#         current_day = datetime.now().weekday()
#         self.historical_new_data_dump = []
#         self.daily_data_dump = []

#         # self.target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
#         # self.destination_date = datetime.now().strftime("%Y-%m-%d")
#         self.destination_date= '2024-07-16'
#         self.spider_directory = 'tenx'
#         self.hash_dumps = []

#     @classmethod
#     def from_crawler(cls, crawler):
#         pipeline = cls()
#         crawler.signals.connect(pipeline.spider_opened, signal=scrapy.signals.spider_opened)
#         crawler.signals.connect(pipeline.spider_closed, signal=scrapy.signals.spider_closed)
#         return pipeline

#     def spider_opened(self, spider):
#         self.start_time = time.time()
#         logger.info(f'Spider Going to Start -----> {spider.name}')

#     def process_item(self, item, spider):
#         logger.info('*** Processing Item ***')
#         hash_name = item.get('hash')
#         self.historical_new_data_dump.append(dict(item))
#         self.daily_data_dump.append(dict(item))  # Collect daily data
#         self.hash_dumps.append(hash_name)
#         return item

#     def spider_closed(self, spider):
#         parquet_upload_path = Path(f'output/historical/{self.spider_directory}/{self.destination_date}/{spider.name}.parquet')
#         json_upload_path = Path(f'output/daily_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.json')
#         hash_file_path = Path(f'output/hash_collections/{self.spider_directory}/{self.destination_date}/{spider.name}.txt')
#         consolidated_historical_path = Path(f'output/consolidated_historical_file/{self.spider_directory}/{spider.name}.parquet')
        
#         parquet_upload_path.parent.mkdir(parents=True, exist_ok=True)
#         json_upload_path.parent.mkdir(parents=True, exist_ok=True)
#         hash_file_path.parent.mkdir(parents=True, exist_ok=True)
#         consolidated_historical_path.parent.mkdir(parents=True, exist_ok=True)
        
#         new_df = pd.DataFrame(self.historical_new_data_dump, dtype=str)
#         final_df = new_df.drop('hash', axis=1)
        
#         with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
#             tmp_paq_path = tmp_file.name
#             final_df.to_parquet(tmp_paq_path, engine='fastparquet', compression='gzip')
#             tmp_file.flush()
#             tmp_file.seek(0)
        
#         shutil.move(tmp_paq_path, parquet_upload_path)
        
#         hash_dump = [element + '\n' for element in self.hash_dumps]
#         with open(hash_file_path, 'w') as temp_file:
#             temp_file.writelines(hash_dump)

#         # Save daily data dump to JSON
#         with open(json_upload_path, 'w', encoding='utf-8') as json_file:
#             json.dump(self.daily_data_dump, json_file, ensure_ascii=False, indent=4)
        
#         logger.info(f'Spider Closed -----> {spider.name}')


