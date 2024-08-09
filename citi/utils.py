import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

def slack_spider_notofication(spider_name,status):
    try:
        logger.info("Enter the slack spider notification function in utils")
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        slack_channel = os.getenv("SLACK_CHANNEL")
        bot = WebClient(slack_bot_token)
        if status == 'Started':
            attachments = [
                {
                    "color": "#DAC511",
                    "blocks": [
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f":rocket: `{spider_name} Spider {status}`"
                                },
                            ]
                        }
                    ]
                }
            ]
        else:
            attachments = [
                {
                    "color": "#1CDA11",
                    "blocks": [
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f":white_check_mark: `{spider_name} Spider {status}`"
                                },
                            ]
                        }
                    ]
                }
            ]
        bot.chat_postMessage(channel=slack_channel, attachments=attachments)
        return True

    except SlackApiError as e:
        error_message = str(e.response['error'])
        attachments = [
            {
                "color": "#DA1130",
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f":x: `{spider_name} Spider got Error {error_message}`"
                            },
                        ]
                    }
                ]
            }
        ]
        bot.chat_postMessage(channel=slack_channel, attachments=attachments)
        logger.info("Error in slack notofication =>", str(e.response['error']))
        return False

def slack_spider_status(spider_name, item_scraped_count, new_record_count, no_record_count, duplicate_record_count, historical_data_count, total_record_count, error_status, finish_status):
    try:
        logger.info("Enter the slack spider status function in utils")
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        slack_channel = os.getenv("SLACK_CHANNEL")
        bot = WebClient(slack_bot_token)
        attachments =  [
            {
                "color": "#D311DA",
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"_Category:_ :heavy_dollar_sign: `Depository Receipt`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Spider Name:_ `{spider_name}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Item Count:_ `{item_scraped_count}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Daily Append Record Count:_ `{new_record_count}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Daily No Record Count:_ `{no_record_count}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Daily Duplicate Record Count:_ `{duplicate_record_count}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Historical Data Count:_ `{historical_data_count}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Total Website Record Count:_ `{total_record_count}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Spider Error Count:_ `{error_status}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"_Status:_ `{finish_status}`"
                            }
                        ]
                    }
                ]
            }
        ]
        bot.chat_postMessage(channel=slack_channel, attachments=attachments)
        return True
    
    except SlackApiError as e:
        error_message = str(e.response['error'])
        logger.info("Error in slack notofication =>", str(e.response['error']))
        attachments = [
            {
                "color": "#DA1130",
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f":x: `{spider_name} Spider Status got Error {error_message}`"
                            },
                        ]
                    }
                ]
            }
        ]
        bot.chat_postMessage(channel=slack_channel, attachments=attachments)
        return False
    
def slack_lambda_notification(status, trigger):
    try:
        logging.info(f"Enter the slack Lambda notification function")
        slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        slack_channel = os.getenv('SLACK_CHANNEL')
        logging.info(f'slack_channel ----> {slack_channel}')
        bot = WebClient(slack_bot_token)
        if trigger == 'Started':
            attachments = [
            {
                "color": "#DAC511",
                "blocks": [ 
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f":alarm_clock: `{status}`"
                            },
                        ]
                    }
                ]
            }]
        else:
            attachments = [
            {
                "color": "#1CDA11",
                "blocks": [ 
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f":alarm_clock: `{status}`"
                            },
                        ]
                    }
                ]
            }]
        bot.chat_postMessage(channel=slack_channel, attachments=attachments)
        return True

    except SlackApiError as e:
        error_message = str(e.response['error'])
        logger.info("Error in slack notofication =>", str(e.response['error']))
        attachments = [
            {
                "color": "#DA1130",
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f":x: `Lambda got Error {error_message}`"
                            },
                        ]
                    }
                ]
            }
        ]
        bot.chat_postMessage(channel=slack_channel, attachments=attachments)
        return False