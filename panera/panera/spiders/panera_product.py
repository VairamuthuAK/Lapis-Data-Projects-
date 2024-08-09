import os 
import scrapy
import json
import hashlib
from datetime import datetime
from panera2.items import (
    RestaurantItem,
    CategoryItem,
    SubCategoryItem,
    ProductItem 
)
from dotenv import load_dotenv

load_dotenv()

class PaneraSpider(scrapy.Spider):
    name = "panera_product"
    count = 1
    log_folder = os.path.join('logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_folder, f"{name}_{current_date}.log")
    error_log_file = os.path.join(log_folder, f"{name}_errors_{current_date}.txt")
 
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         'panera2.pipelines.Panera2Pipeline': 300,
    #     },
    #     'FEED_EXPORT_ENCODING': 'utf-8',
    #     'LOG_FILE': log_file,
    #     'LOG_LEVEL': 'INFO',
    #     'FEEDS': {f"s3://lapis-lupine-lambda-output-files/output/daily_collections/panera/{current_date}/{name}.json": {"format": "json"}},  
    # } 

    def start_requests(self):
        # states_code = ['AL']
        states_code = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        for state in states_code[:1]:
            print(f'state----->, {state}')
            start_url = f'https://www-api.panerabread.com/www-api/public/cafe/location/{state.lower()}'
            states_headers = {
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
                'Accept-Encoding': 'gzip',
            }
            yield scrapy.Request(start_url, method='GET', headers=states_headers, callback=self.parse)

    def parse(self, response):
        # breakpoint()
        payload_data = json.loads(response.text)
        for data in payload_data[:1]:
            city = data['city']
            print(f'city------->{city}')
            for cafe in data['cafes'][:2]:
                cafeId = cafe.get('cafeId', '')
                city = cafe.get('city', '')
                countryCode = cafe.get('countryCode', '')
                name = cafe.get('name', '')
                latitude = cafe.get('latitude', '')
                longitude = cafe.get('longitude', '')
                state = cafe.get('state', '')
                streetName = cafe.get('streetName', '')
                payload_address = f'{city}, {state} {countryCode}'
                main_url = "https://www-api.panerabread.com/www-api/public/cafe/search?openCafes=true"
                payload = {
                    "address": f"{payload_address}",
                    "radius": 24000,
                    "latitude": latitude,
                    "longitude": longitude
                }
                main_headers = {
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
                    'Accept-Encoding': 'gzip',
                }
                yield scrapy.Request(main_url, method='POST', headers=main_headers, body=json.dumps(payload), callback=self.parse_1)

    def parse_1(self, response):
        # breakpoint()
        print('Response Status URL----->',response.status)
        json_data = json.loads(response.text)
        for data_1 in json_data.get("cafeList", []):
            restaurant_item = RestaurantItem()
            restaurant_item["restaurant_id"] = data_1.get("cafeId", "")
            restaurant_item["restaurant_location"] = data_1.get("cafeLocation", "").get("city", "")
            restaurant_item["location_url"] = "https://www.panerabread.com/en-us/app/menu.html"
            menu_url = f'https://mobile-adapter.cloud.panerabread.com/www-api/public/menu/v2/versions/{restaurant_item["restaurant_id"]}'
            menu_headers = {
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
            yield scrapy.Request(menu_url, method='GET', headers=menu_headers, callback=self.parse_2, cb_kwargs={"restaurant_item": restaurant_item})

    def parse_2(self, response, restaurant_item): 
        # breakpoint()
        link_data = json.loads(response.text)
        Category = link_data.get('versions', '').get('mnavCategory', '')
        CategorySchedule = link_data.get('versions', '').get('mnavCategorySchedule', '')
        productCombo = link_data.get('versions', '').get('productCombo', '')
        categories_link = f'https://www-api.panerabread.com/www-api/public/menu/categories/{restaurant_item["restaurant_id"]}/version/{Category}/{CategorySchedule}/{productCombo}/en-US?cloud=false'
        categories_headers = {
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
        yield scrapy.Request(categories_link, headers=categories_headers, callback=self.parse_3, cb_kwargs={"restaurant_item": restaurant_item})

    async def parse_3(self, response, restaurant_item):
        menus = []
        data_1 = json.loads(response.text)
        hashes_url = f'https://www-api.panerabread.com/www-api/public/menu/versions/{restaurant_item["restaurant_id"]}?cloud=false'
        hashes_response = await self.request_process(hashes_url)
        hashkey_json_data = json.loads(hashes_response.text)
        # breakpoint()
        category_names_to_check = ["Sandwiches", "Salads", "Soups & Mac", "Kids", "Bakery", "Beverages", "Breakfast", "Family Feast Value Meals", "Value Duets", "Sides & Spreads", "eGift Cards", "Vegetarian"]
        
        for key, data in data_1["categoryDict"].items():
            data_name = data.get("name")
            if data_name in category_names_to_check and data.get("subCategories", []) != []:
                category_item = CategoryItem()
                category_item["category_id"] = data.get("catId")
                category_item["category_name"] = data.get("name")
                category_item["subcategories"] = []

                for cat in data.get("subCategories", []):
                    sub_cat = SubCategoryItem()
                    sub_cat['subcategory_id'] = cat.get('catId', '')
                    sub_cat['subcategory_name'] = data_1["categoryDict"][str(cat.get('catId', ''))].get('name', '')
                    sub_cat['products'] = []

                    for key, sub_data in data_1["categoryDict"].items():
                        if sub_cat['subcategory_id'] == sub_data.get("catId", ""):
                            placard_list = sub_data.get("placards", [])
                            hashes = hashkey_json_data.get('versions', '').get('menuPDP', '')
                            hashkey_api_url = f'https://www-api.panerabread.com/www-api/public/menu/placard/hashes/v2/{restaurant_item["restaurant_id"]}/version/{hashes}/en-US?cloud=false'
                            print('Response Status URL----->',hashkey_api_url)
                            hashkey_response = await self.request_process(hashkey_api_url)
                            try:
                                hashkey_json_data_1 = json.loads(hashkey_response.text)
                                # breakpoint()
                                for key_hash, data_hash in hashkey_json_data_1["placardHashes"].items():
                                    if int(key_hash) in placard_list:
                                        product_item = ProductItem()
                                        product_api_url = f'https://www-api.panerabread.com/www-api/public/menu/placard/hash/{data_hash}'
                                        print('Response Data Main URL----->',product_api_url)
                                        product_response = await self.request_process(product_api_url)
                                        print('Response Data ------->',product_response.status)
                                        try:
                                            product_json_data = json.loads(product_response.text)
                                            
                                            product_item["menu_item_id"] = product_json_data.get('productId')
                                            product_item["menu_item_name"] = product_json_data.get('name')
                                            product_item["menu_item_description"] = product_json_data.get('description')
                                            product_item["menu_item_url"] = f"https://www.panerabread.com/en-us/app/product/{data_hash}.html"
                                            formatted_price = product_json_data.get('price')
                                            if formatted_price:
                                                product_item['menu_item_price'] = f"${formatted_price:.2f}"
                                            else:
                                                product_item['menu_item_price'] = " "
                                            
                                            for img in product_json_data["optSets"]:
                                                product_item['menu_item_ingredients'] = img.get('ingStmnt', '')
                                                if product_json_data.get('name') == img.get('name'):
                                                    product_item["menu_item_image"] = f"https://www.panerabread.com/content/dam/panerabread/menu-omni/integrated-web/detail/{img.get('imgKey')}.jpg"
                                                for cal in img["nutrients"]:
                                                    if cal.get("name") == "Calories":
                                                        product_item["menu_item_calories"] = int(cal.get('value'))
                                            
                                            sub_cat['products'].append(product_item)
                                        except:
                                            with open(f'product_error_link_collection{self.current_date}.txt','a')as f:
                                                f.write(product_response.url + '\n')
                            except:
                                pass
                    category_item['subcategories'].append(sub_cat)
                
                menus.append(category_item)

        restaurant_item["menus"] = menus
        all_values = [str(restaurant_item[key]) for key in dict(restaurant_item) if key != 'images' and key != 'scraped_date']
        hash_obj = hashlib.md5(('_'.join(all_values)).encode('utf-8'))
        hash = hash_obj.hexdigest()
        restaurant_item['hash'] = hash
        restaurant_item['scraped_date']= datetime.now().strftime("%Y%m%d")
        yield restaurant_item

    async def request_process(self, url):
            # api_headers = {'referer': 'https://www.panerabread.com/'}
            base_headers = {
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
                                    'Accept-Encoding': 'gzip',
                                    }
            request = scrapy.Request(url,headers=base_headers)
            response = await self.crawler.engine.download(request)
            return response