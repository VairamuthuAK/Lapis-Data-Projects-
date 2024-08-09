# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from urllib.parse import urldefrag
import scrapy
from scrapy.http.request.form import _urlencode


class RestaurantScheduleItem(scrapy.Item):
    type = scrapy.Field()
    monday = scrapy.Field()
    tuesday = scrapy.Field()
    wednesday = scrapy.Field()
    thursday = scrapy.Field()
    friday = scrapy.Field()
    saturday = scrapy.Field()
    sunday = scrapy.Field()
    restaurant_working_hours=scrapy.Field()



class RestaurantpaneraItem(scrapy.Item):
    # source_id = scrapy.Field()
    restaurant_id=scrapy.Field()
    location_url = scrapy.Field()
    restaurant_location = scrapy.Field()
    phone_number = scrapy.Field()
    street_address = scrapy.Field()
    locality = scrapy.Field()
    city = scrapy.Field()
    postal_code = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()
    menus: list = scrapy.Field()


class CategoryItem(scrapy.Item):
    category_id = scrapy.Field()
    category_name = scrapy.Field()
    subcategories = scrapy.Field()

class SubCategoryItem(scrapy.Item):
    subcategory_id = scrapy.Field()
    subcategory_name = scrapy.Field()
    products = scrapy.Field()

class ProductItem(scrapy.Item):
    menu_item_id = scrapy.Field()
    menu_item_name = scrapy.Field()
    menu_item_description = scrapy.Field()
    menu_item_url = scrapy.Field()
    menu_item_price = scrapy.Field()
    menu_item_ingredients = scrapy.Field()
    menu_item_image = scrapy.Field()
    menu_item_calories = scrapy.Field()
    hash=scrapy.Field()


class RestaurantItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    restaurant_location = scrapy.Field()
    location_url = scrapy.Field()
    menus = scrapy.Field()
    phone_number = scrapy.Field()
    street_address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    postal_code = scrapy.Field()
    country = scrapy.Field()  # Remove the stray backslash here
    location_name=scrapy.Field()
    restaurant_working_hours=scrapy.Field()
    hash=scrapy.Field()
