import os 
import scrapy 
import json 
import dateutil.parser as parser
import hashlib
from datetime import datetime
from panera2.items import (
    RestaurantItem,
    RestaurantScheduleItem
)
from dotenv import load_dotenv

load_dotenv()


class PaneraSpider(scrapy.Spider):
    name = "panera_location"
    count = 1
    seen_cafe_ids = set()  
    log_folder = os.path.join('logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_folder, f"{name}_{current_date}.log")
    error_log_file = os.path.join(log_folder, f"{name}_errors_{current_date}.txt")

    custom_settings = {
        'ITEM_PIPELINES': {
            'panera2.pipelines.Panera2Pipeline': 300,
        },
        'FEED_EXPORT_ENCODING': 'utf-8',
        'LOG_FILE': log_file,
        'LOG_LEVEL': 'INFO'
       } 



    def start_requests(self):
        states_code = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        for state in states_code:
            print(f'State: {state}')
            start_url = f'https://www-api.panerabread.com/www-api/public/cafe/location/{state.lower()}'
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'origin': 'https://www.panerabread.com',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://www.panerabread.com/',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'x-origin-source': 'iWeb',
            }
            yield scrapy.Request(start_url, method='GET', headers=headers, callback=self.parse)

    def parse(self, response):
        payload_data = json.loads(response.text)
        for data in payload_data:
            city = data['city']
            print(f'City: {city}')
            for cafe in data['cafes']:
                cafe_id = cafe.get('cafeId', '')
                if cafe_id in self.seen_cafe_ids:
                    continue  # Skip already seen cafe ID
                self.seen_cafe_ids.add(cafe_id)
                city = cafe.get('city', '')
                country_code = cafe.get('countryCode', '')
                name = cafe.get('name', '')
                latitude = cafe.get('latitude', '')
                longitude = cafe.get('longitude', '')
                state = cafe.get('state', '')
                payload_address = f'{city}, {state} {country_code}'
                
                main_url = "https://www-api.panerabread.com/www-api/public/cafe/search?openCafes=true"
                payload = {
                    "address": f"{payload_address}",
                    "radius": 24000,
                    "latitude": latitude,
                    "longitude": longitude
                }
                headers = {
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json;charset=UTF-8',
                    'origin': 'https://www.panerabread.com',
                    'pragma': 'no-cache',
                    'priority': 'u=1, i',
                    'referer': 'https://www.panerabread.com/',
                    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                    'x-origin-source': 'iWeb',
                }

                yield scrapy.Request(main_url, method='POST', headers=headers, body=json.dumps(payload), callback=self.parse_1)

    def parse_1(self, response):
        data = json.loads(response.text)
        for cafe in data.get("cafeList", []):
            cafe_id = cafe.get("cafeId", "")
            if cafe_id in self.seen_cafe_ids:
                continue  # Skip already seen cafe ID
            self.seen_cafe_ids.add(cafe_id)
            
            restaurant_item = RestaurantItem()
            restaurant_item["restaurant_id"] = cafe_id
            restaurant_item["location_name"] = cafe.get("cafeLocation", {}).get("city", "")
            restaurant_item["location_url"] = "https://www.panerabread.com/en-us/app/menu.html"
            restaurant_item["phone_number"] = cafe.get("cafePhone", "")
            restaurant_item["street_address"] = cafe.get("cafeLocation", {}).get("addressLine1", "")
            restaurant_item["city"] = cafe.get("cafeLocation", {}).get("city", "")
            restaurant_item["state"] = cafe.get("cafeLocation", {}).get("countryDivision", "")
            restaurant_item["postal_code"] = cafe.get("cafeLocation", {}).get("postalCode", "")
            restaurant_item["country"] = "US"
            
            restaurant_working_hours = []
            schedule_item = RestaurantScheduleItem()
            for day_key, day_schedule in cafe.get('cafeHours', {}).get('delivery', {}).get('hours', {}).items():
                if day_schedule:
                    weekday = parser.parse(day_key).strftime('%A').lower()
                    if weekday in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
                        start = parser.parse(day_schedule[0].get('open')).strftime('%H:%M %p')
                        end = parser.parse(day_schedule[0].get('close')).strftime('%I:%M %p')
                        schedule_description = f"{start} - {end}"
                        schedule_item[weekday] = schedule_description
            restaurant_working_hours.append(schedule_item)
            restaurant_item["restaurant_working_hours"] = restaurant_working_hours
            all_values = [str(restaurant_item[key]) for key in dict(restaurant_item) if key != 'images']
            hash_obj = hashlib.md5(('_'.join(all_values)).encode('utf-8'))
            hash = hash_obj.hexdigest()
            restaurant_item['hash'] = hash
            yield restaurant_item
