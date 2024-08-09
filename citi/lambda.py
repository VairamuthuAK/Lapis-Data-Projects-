from scrapy.crawler import CrawlerRunner, CrawlerProcess
from twisted.internet import reactor, defer
from spiders.adrciti_corporate import AdrCitiCorporateSpider
from spiders.adrciti_divsdistributions import AdrCitiDivsandDistributionSpider
from spiders.adrciti_dsfdistributions import AdrCitiDsfDistributionsSpider
from spiders.adrciti_openclosed import AdrCitiOpenClosedSpider
from spiders.adrciti_universe import AdrCitiUniverseSpider
from spiders.adrkorean_equitiesexchange import AdrKoreanEquitiesExchangeSpider
from spiders.adrciti_twse import AdrCitiTwseSpider
from spiders.adrciti_india import AdrcitiIndiaSpider
from scrapy.utils.project import get_project_settings
from twisted.internet.task import deferLater
from utils import slack_lambda_notification
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LambdaCrawler:
    def __init__(self):
        self.crawling = False
        self.process = CrawlerProcess(get_project_settings())
        self.queue = []

    @defer.inlineCallbacks
    def crawl(self, spider_cls):
        yield self.process.crawl(spider_cls)
        self.crawling = False
        if self.queue:
            next_spider = self.queue.pop(0)
            self.start_crawl(next_spider)

    def start_crawl(self, spider_cls):
        if not self.crawling:
            self.crawling = True
            d = self.crawl(spider_cls)
            d.addBoth(lambda _: self.stop_reactor())
            if not reactor.running:
                reactor.run(installSignalHandlers=False)
        else:
            self.queue.append(spider_cls)

    def stop_reactor(self):
        if reactor.running:
            reactor.stop()

lambda_crawler = LambdaCrawler()

def time_zone():
    current_time_utc = datetime.now(pytz.utc)
    est = pytz.timezone('US/Eastern')
    current_time_est = current_time_utc.astimezone(est)
    current_time_est_str = current_time_est.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return str(current_time_est_str)

def lambda_handler(event, context):
    data = {
        "citi_corporate": AdrCitiCorporateSpider,
        "citi_divsanddistributions": AdrCitiDivsandDistributionSpider,
        "citi_dsfdistributions": AdrCitiDsfDistributionsSpider,
        "citi_openclosed": AdrCitiOpenClosedSpider,
        "citi_universe": AdrCitiUniverseSpider,
        "citi_equitiesexchange": AdrKoreanEquitiesExchangeSpider,
        "citi_twse": AdrCitiTwseSpider,
        "citi_india": AdrcitiIndiaSpider,
    }

    spider_name = event.get('spider')
    if spider_name not in data:
        logging.info('No spider name Found !!')
        return {
            "status_code": '400',
            "message": f'Spider {spider_name} not found!'
        }

    else:
        try:
            current_time_est_str = time_zone()
            logging.info(f"Start the lambda function {spider_name} and start time is {current_time_est_str}")
            status = f"{str(spider_name)} lambda is started and time is {current_time_est_str}"
            lambda_start = slack_lambda_notification(status, 'Started')
            if lambda_start:
                logging.info('Lambda Slack Message Send Successfully !!!!')
            else:
                logging.info('Lambda Slack Message Send Failed !!!!')
            lambda_crawler.start_crawl(data[spider_name])
            current_time_est_str = time_zone()
            status = f"{str(spider_name)} lambda is completed and time is {current_time_est_str}"
            lambda_finish = slack_lambda_notification(status, 'Completed')
            if lambda_finish:
                logging.info('Lambda Slack Message Send Successfully !!!!')
            else:
                logging.info('Lambda Slack Message Send Failed !!!!')
            return {
                "status_code": '200',
                "message": f'{data[spider_name].name} Scrapy spider executed successfully!',
            }
        except Exception as e:
            logging.info(f"Error the lambda function {e}")
            raise e