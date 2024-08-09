import logging
from scrapy.utils.log import configure_logging
# from twisted.internet import reactor
# from twisted.internet.threads import deferToThread
from playwright.sync_api import sync_playwright
from datetime import datetime
import scrapy
import hashlib
import codecs
import html
import time
from parsel import Selector
import re


def remove_key(data):
    if str(data).strip() == "-":
        return None
    else:
        return data

class BoosiniSpider(scrapy.Spider):
    name = "tenx"

    custom_settings = {
        'ITEM_PIPELINES': {
            'tenx.pipeline.TenxPipeline': 300,
        },
    }
    
    def start_requests(self):
        url = "https://www.google.com/"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self,response):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)  # Launch browser in non-headless mode
            context = browser.new_context()
            page = context.new_page()

            page.goto("https://www.ten-x.com/",timeout = 0)
            page.locator('//a[@data-elm-id="POPUP_MENU_LOGIN"]').click()
            time.sleep(10)
            fill_box = page.locator('//input[@name="email"]')
            fill_box.fill("loyise6216@digdy.com")
            page.locator('//button[@type="submit"]').click()
            time.sleep(10)
            fill_box = page.locator("//input[@id = 'password']")
            fill_box.fill("Asdfghqw")
            page.locator('//button[@id="loginButton"]').click()
            time.sleep(10)
            page.locator('//a[@data-elm-id="view-all-btn"]').click()
            time.sleep(10)
            page.wait_for_load_state('load')
            page.locator('//div[@class="input-container_styles_mUY3"]/div[1]//span').wait_for(state='visible', timeout=60000)
            page.locator('//div[@class="input-container_styles_mUY3"]/div[1]//span').click()
            time.sleep(10)
            page.locator('//li[contains(text(),"View All")]').click()
            time.sleep(5)
            content =  page.content()
            response = Selector(text=content)
            links = response.xpath('//div[@data-elm-id="Asset_List_View"]//a[@data-elm-id="property-item"]/@href').getall()
            for link in links:
                item={}
                new_page =  context.new_page()
                new_page.goto(link, timeout=0)
                content1 =  new_page.content()
                response = Selector(text=content1)
                item['source_url']=link
                item['name']=response.xpath('//h1[@data-elm-id="prop_name"]//text()').get()
                item['asset_type']=response.xpath('//span[@data-elm-id="asset_type_content"]//text()').get()
                primary_property_type_1=response.xpath('//span[@data-elm-id="condo_primary_type_content"]//text()').get()
                primary_property_type_2=response.xpath('//span[@data-elm-id="primary_type_content"]//text()').get()
                if primary_property_type_1:
                    item['primary_property_type']=primary_property_type_1
                elif primary_property_type_2:
                    item['primary_property_type']=primary_property_type_2
                else:
                    item['primary_property_type']=None 
            
                item['primary_sub_type']=response.xpath('//span[@data-elm-id="primary_sub_type_content"]//text()').get()

                property_address=response.xpath('//span[@data-elm-id="prop_address"]//text()').get()
                if property_address:
                    item['property_address']=property_address
                else:
                    property_info={}                
                    property_address_1 = response.xpath('//div[@class="ant-row investment-oportunity-address_styles_PR3J"]')
                    for index, property in enumerate(property_address_1,1):
                        property_info[f'property_address_{index}'] =property.xpath('.//div[1]/text()').get()
                        property_info[f'property_type_{index}'] =property.xpath('.//div[2]/text()').get()
                        property_info[f'property_size_{index}_(sq.ft.)'] =property.xpath('.//div[3]/text()').get().replace('(Sq. Ft.)','')
                    item['property_info']=property_info

                item['offering_size_sq_ft']=response.xpath('//span[@data-elm-id="offering_size_content"]//text()').get()
                item['starting_bid']=response.xpath('//span[@data-elm-id="mobile_start_bid_amount"]//text()').get()
                item['online_auction']=response.xpath('//span[@data-elm-id="bidding-box-auction-dates-value"]//text()').get()
                item['event_item']=response.xpath('//span[@data-elm-id="event-item"]//text()').get()
                item['units']=response.xpath('//span[@data-elm-id="units_content"]//text()').get()
                item['building_size_sq_ft']=response.xpath('//span[@data-elm-id="building_size_content"]//text()').get()
                year_built=response.xpath('//span[@data-elm-id="year_built_content"]//text()').get()
                if year_built:
                    item['year_built']=year_built
                else:
                    item['year_built']=response.xpath('//span[@data-elm-id="mobile_year_built"]//text()').get()
                item['occupancy']=response.xpath('//span[@data-elm-id="occupancy_content"]//text()').get()
                item['type_of_ownership']=response.xpath('//span[@data-elm-id="type_of_ownership"]//text()').get()
                item['lot_size_acres']=response.xpath('//span[@data-elm-id="lot_size_content"]//text()').get()
                item['floors']=response.xpath('//span[@data-elm-id="mobile_floors"]//text()').get()
                item['assessor_parcel_number']=response.xpath('//span[@data-elm-id="mobile_apn"]//text()').get()
                property_id=response.xpath('//span[@data-elm-id="property_id"]//text()').get()
                if property_id:
                    item['property_id']=property_id
                else:
                    item['property_id']=response.xpath('//span[@data-elm-id="property-id"]//text()').get()
                item['building_class']=response.xpath('//span[@data-elm-id="mobile_building_class"]//text()').get()
                item['starting_bid']=response.xpath('//span[@data-elm-id="mobile_start_bid_amount"]//text()').get()
                item['year_renovated']=response.xpath('//span[@data-elm-id="mobile_year_renovated"]//text()').get()
                item['zoning_designation']=response.xpath('//span[@data-elm-id="mobile_zoning_designation"]//text()').get()
                item['parking_ratio']=response.xpath('//span[@data-elm-id="mobile_parking_ratio"]//text()').get()
                item['parking_count']=response.xpath('//span[@data-elm-id="mobile_parking_count"]//text()').get()
                item['common_amenities']=response.xpath('//span[@data-elm-id="mobile_common_amenities"]//text()').get()
                item['unit_amenities']=response.xpath('//span[@data-elm-id="mobile_unit_amenities"]//text()').get()
                item['rooms']=response.xpath('//span[@data-elm-id="mobile_rooms"]//text()').get()
                item['building_coverage_ratio']=response.xpath('//span[@data-elm-id="mobile_coverage_ratio"]//text()').get()
                item['scraped_date']= datetime.now().strftime("%Y%m%d")
                # item['description']=response.xpath('//div[@class="detailed-desc-container"]//p/text()').get().replace('\n','')
                description = response.xpath('//div[@class="detailed-desc-container"]//p/text()').get()
                if description:
                    # decoded_description = codecs.decode(description, 'unicode_escape').replace('\n', '')
                    cleaned_description = html.unescape(description).replace('\n', '')
                    item['description'] = cleaned_description
                else:
                    item['description'] = ''
                item['property_information']=''.join(response.xpath('//h4[contains(text(), "Property Information")]/following-sibling::div[@data-elm-id="property-info-highlights"]/div/text()').getall()).strip()
                all_images=[]
                if re.search(r'media_uri\"\:\"(.*?)\s*\"\}',content1):
                    img = re.findall(r'media_uri\"\:\"(.*?)\s*\"\}',content1)
                    for images in img:
                        if len(images) > 50:
                            all_images.append(images)
                item['images']= all_images
                try:
                    new_page.wait_for_selector('//div[@role="tab"][2]', timeout=0)
                    new_page.locator('//div[@role="tab"][2]').click()
                    time.sleep(10)
                    content2 =  new_page.content()
                    response = Selector(text=content2)
                    item['total_market_value']=response.xpath('//div[contains(text(),"Total Market Value")]//following-sibling::div/text()').get()
                    item['twoval_months_sales_volume']=response.xpath('//div[contains(text(),"12 Mo Sales Volume")]//following-sibling::div/text()').get()
                    transactions = response.xpath('//tr[@data-row-key="Transactions"]/td/text()').getall()
                    if len(transactions) > 3: 
                        item['transactions_total'] =remove_key(transactions[1])
                        item['transactions_lowest']=remove_key(transactions[2])
                        item['transactions_highest']=remove_key(transactions[3])
                    else:
                        item['transactions_total']=None
                        item['transactions_lowest']=None
                        item['transactions_highest']= None

                    sales_volume=response.xpath('//tr[@data-row-key="Sales Volume"]/td/text()').getall()
                    if len(sales_volume) > 3:
                        item['sales_volume_total']=remove_key(sales_volume[1])
                        item['sales_volume_lowest']=remove_key(sales_volume[2])
                        item['sales_volume_highest']=remove_key(sales_volume[3])
                    else:
                        item['sales_volume_total']=None
                        item['sales_volume_lowest']=None
                        item['sales_volume_highest']=None

                    properties_sold=response.xpath('//tr[@data-row-key="Properties Sold"]/td/text()').getall()
                    if len(properties_sold) > 3 :
                        item['properties_sold_total']=remove_key(properties_sold[1])
                        item['properties_sold_lowest']=remove_key(properties_sold[2])
                        item['properties_sold_highest']=remove_key(properties_sold[3])
                    else:
                        item['properties_sold_total']=None
                        item['properties_sold_lowest']=None
                        item['properties_sold_highest']=None

                    transacted_units=response.xpath('//tr[@data-row-key="Transacted Units"]/td/text()').getall()
                    if len(transacted_units) > 3:
                        item['transacted_units_total']=remove_key(transacted_units[1])
                        item['transacted_units_lowest']=remove_key(transacted_units[2])
                        item['transacted_units_highest']=remove_key(transacted_units[3])
                    else:
                        item['transacted_units_total']=None
                        item['transacted_units_lowest']=None
                        item['transacted_units_highest']=None

                    transacted_sf=response.xpath('//tr[@data-row-key="Transacted SF"]/td/text()').getall()
                    if len(transacted_sf) > 3:
                        item['transacted_sf_total']=remove_key(transacted_sf[1])
                        item['transacted_sf_lowest']=remove_key(transacted_sf[2])
                        item['transacted_sf_highest']=remove_key(transacted_sf[3])
                    else:
                        item['transacted_sf_total']=None
                        item['transacted_sf_lowest']=None
                        item['transacted_sf_highest']=None

                    transacted_room=response.xpath('//tr[@data-row-key="Transacted Rooms"]/td/text()').getall()
                    if len(transacted_room) > 3:
                        item['transacted_room_total']=remove_key(transacted_room[1])
                        item['transacted_room_lowest']=remove_key(transacted_room[2])
                        item['transacted_room_highest']=remove_key(transacted_room[3])
                    else:
                        item['transacted_room_total']=None
                        item['transacted_room_lowest']=None
                        item['transacted_room_highest']=None

                    avarage_units=response.xpath('//tr[@data-row-key="Average Units"]/td/text()').getall()
                    if len(avarage_units) > 3:
                        item['avarage_units_total']=remove_key(avarage_units[1])
                        item['avarage_units_lowest']=remove_key(avarage_units[2])
                        item['avarage_units_highest']=remove_key(avarage_units[3])
                    else:
                        item['avarage_units_total']=None
                        item['avarage_units_lowest']=None
                        item['avarage_units_highest']=None

                    avarage_room=response.xpath('//tr[@data-row-key="Average Rooms"]/td/text()').getall()
                    if len(avarage_room) > 3:
                        item['avarage_room_total']=remove_key(avarage_room[1])
                        item['avarage_room_lowest']=remove_key(avarage_room[2])
                        item['avarage_room_highest']=remove_key(avarage_room[3])
                    else:
                        item['avarage_room_total']=None
                        item['avarage_room_lowest']=None
                        item['avarage_room_highest']=None

                    avarage_sf=response.xpath('//tr[@data-row-key="Average SF"]/td/text()').getall()
                    if len(avarage_sf) > 3:
                        item['avarage_sf_total']=remove_key(avarage_sf[1])
                        item['avarage_sf_lowest']=remove_key(avarage_sf[2])
                        item['avarage_sf_highest']=remove_key(avarage_sf[3])
                    else:
                        item['avarage_sf_total']=None
                        item['avarage_sf_lowest']=None
                        item['avarage_sf_highest']=None

                    # breakpoint()
                    item['avarage_market_cap_rate']=response.xpath('//div[contains(text(),"Avg Market Cap Rate")]//following-sibling::div/text()').get()
                    mkt_sale_price_unit_chg_yoy=response.xpath('//div[contains(text(),"Mkt Sale Price/Unit Chg (YOY)")]//following-sibling::div/text()').get()
                    Mkt_sale_price_sf_chg_yoy=response.xpath('//div[contains(text(),"Mkt Sale Price/SF Chg (YOY)")]//following-sibling::div/text()').get()
                    if mkt_sale_price_unit_chg_yoy:
                        item['mkt_sale_price_unit_chg_yoy']=mkt_sale_price_unit_chg_yoy
                    elif Mkt_sale_price_sf_chg_yoy:
                        item['mkt_sale_price_unit_chg_yoy']=Mkt_sale_price_sf_chg_yoy
                    else:
                        item['mkt_sale_price_unit_chg_yoy']=response.xpath('//div[contains(text(),"Mkt Sale Price/Room Chg (YOY)")]//following-sibling::div/text()').get()

                    cap_rate=response.xpath('//tr[@data-row-key="Cap Rate"]/td/text()').getall()
                    if len(cap_rate) > 4:
                        item['cap_rate_avarage']=remove_key(cap_rate[1])
                        item['cap_rate_lowest']=remove_key(cap_rate[2])
                        item['cap_rate_highest']=remove_key(cap_rate[3])
                        item['cap_rate_market']=remove_key(cap_rate[4])
                    else:
                        item['cap_rate_avarage']=None
                        item['cap_rate_lowest']=None
                        item['cap_rate_highest']=None
                        item['cap_rate_market']=None

                    sale_price_units=response.xpath('//tr[@data-row-key="Sale Price/Unit"]/td/text()').getall()
                    if len(sale_price_units) > 4:
                        item['sale_price_unit_avarage']=remove_key(sale_price_units[1])
                        item['sale_price_unit_lowest']=remove_key(sale_price_units[2])
                        item['sale_price_unit_highest']=remove_key(sale_price_units[3])
                        item['sale_price_unit_market']=remove_key(sale_price_units[4])
                    else:
                        item['sale_price_unit_avarage']=None
                        item['sale_price_unit_lowest']=None
                        item['sale_price_unit_highest']=None
                        item['sale_price_unit_market']=None

                    sale_price_room=response.xpath('//tr[@data-row-key="Sale Price/Room"]/td/text()').getall()
                    if len(sale_price_room) > 4:
                        item['sale_price_room_avarage']=remove_key(sale_price_room[1])
                        item['sale_price_room_lowest']=remove_key(sale_price_room[2])
                        item['sale_price_room_highes']=remove_key(sale_price_room[3])
                        item['sale_price_room_market']=remove_key(sale_price_room[4])
                    else:
                        item['sale_price_room_avarage']=None
                        item['sale_price_room_lowest']=None
                        item['sale_price_room_highes']=None
                        item['sale_price_room_market']=None

                    sale_price_sf=response.xpath('//tr[@data-row-key="Sale Price/SF"]/td/text()').getall()
                    if len(sale_price_sf) > 4:
                        item['sale_price_sf_avarage']=remove_key(sale_price_sf[1])
                        item['sale_price_sf_lowest']=remove_key(sale_price_sf[2])
                        item['sale_price_sf_highes']=remove_key(sale_price_sf[3])
                        item['sale_price_sf_market']=remove_key(sale_price_sf[4])
                    else:
                        item['sale_price_sf_avarage']=None
                        item['sale_price_sf_lowest']=None
                        item['sale_price_sf_highes']=None
                        item['sale_price_sf_market']=None

                    sale_price=response.xpath('//tr[@data-row-key="Sale Price"]/td/text()').getall()
                    if len(sale_price) > 4:
                        item['sale_price_avarage']=remove_key(sale_price[1])
                        item['sale_price_lowest']=remove_key(sale_price[2])
                        item['sale_price_highest']=remove_key(sale_price[3])
                        item['sale_price_market']=remove_key(sale_price[4])
                    else:
                        item['sale_price_avarage']=None
                        item['sale_price_lowest']=None
                        item['sale_price_highest']=None
                        item['sale_price_market']=None

                    sale_vs_asking_price=response.xpath('//tr[@data-row-key="Sale vs Asking Price"]/td/text()').getall()
                    if len(sale_vs_asking_price) > 4:
                        item['sale_vs_asking_price_avarage']=remove_key(sale_vs_asking_price[1])
                        item['sale_vs_asking_price_lowest']=remove_key(sale_vs_asking_price[2])
                        item['sale_vs_asking_price_highest']=remove_key(sale_vs_asking_price[3])
                        item['sale_vs_asking_price_market']=remove_key(sale_vs_asking_price[4])
                    else:
                        item['sale_vs_asking_price_avarage']=None
                        item['sale_vs_asking_price_lowest']=None
                        item['sale_vs_asking_price_highest']=None
                        item['sale_vs_asking_price_market']=None
                    
                    leased_at_sale=response.xpath('//tr[@data-row-key="% Leased at Sale"]/td/text()').getall()
                    if len(leased_at_sale) > 4:
                        item['leased_at_sale_avarage']=remove_key(leased_at_sale[1])
                        item['leased_at_sale_lowest']=remove_key(leased_at_sale[2])
                        item['leased_at_sale_highest']=remove_key(leased_at_sale[3])
                        item['leased_at_sale_market']=remove_key(leased_at_sale[4])
                    else:
                        item['leased_at_sale_avarage']=None
                        item['leased_at_sale_lowest']=None
                        item['leased_at_sale_highest']=None
                        item['leased_at_sale_market']=None

                    months_to_sale=response.xpath('//tr[@data-row-key="Months To Sale"]/td/text()').getall()
                    if len(months_to_sale) > 4:
                        item['months_to_sale_avarage']=remove_key(months_to_sale[1])
                        item['months_to_sale_lowest']=remove_key(months_to_sale[2])
                        item['months_to_sale_highest']=remove_key(months_to_sale[3])
                        item['months_to_sale_market']=remove_key(months_to_sale[4])
                    else:
                        item['months_to_sale_avarage']=None
                        item['months_to_sale_lowest']=None
                        item['months_to_sale_highest']=None
                        item['months_to_sale_market']=None

                    all_values=[str(value) for key, value in item.items() if key != 'image' and key != 'scraped_date']
                    # all_values = [str(item[key]) for key in item if key != 'images']
                    hash_obj = hashlib.md5(('_'.join(all_values)).encode('utf-8'))
                    hash = hash_obj.hexdigest()
                    item['hash'] = hash
                    # context.close()
                    new_page.close()
                    yield item
                    # breakpoint()
                except :
                    new_page.close()
            #     yield item
            # context.close()
            browser.close()