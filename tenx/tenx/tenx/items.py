# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class TenxItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

class TenxItem(scrapy.Item):
    source_url=scrapy.Field()
    name=scrapy.Field()
    asset_type=scrapy.Field()
    # online_auction=scrapy.Field()
    primary_property_type=scrapy.Field()
    type_of_ownership=scrapy.Field()
    primary_sub_type=scrapy.Field()
    year_renovated=scrapy.Field()
    floors=scrapy.Field()
    lot_size_acres=scrapy.Field()
    property_address=scrapy.Field()
    offering_size_sq_ft=scrapy.Field()
    starting_bid=scrapy.Field()
    units=scrapy.Field()
    building_size_sq_ft=scrapy.Field()
    year_built=scrapy.Field()
    occupancy=scrapy.Field()
    assessor_parcel_number=scrapy.Field()
    property_id=scrapy.Field()
    building_class=scrapy.Field()
    zoning_designation=scrapy.Field()
    parking_ratio=scrapy.Field()
    parking_count=scrapy.Field()
    common_amenities=scrapy.Field()
    unit_amenities=scrapy.Field()
    rooms=scrapy.Field()
    property_info=scrapy.Field()
    building_coverage_ratio=scrapy.Field() 
    images=scrapy.Field()
    event_item=scrapy.Field()
    description=scrapy.Field()
    property_information=scrapy.Field()
    key_metrics=scrapy.Field()
    key_metrics_1=scrapy.Field()
    hash=scrapy.Field()
    scraped_date=scrapy.Field()
