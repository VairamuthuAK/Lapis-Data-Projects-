# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CitiUniverseItem(scrapy.Item):
    issuer=scrapy.Field()
    active=scrapy.Field()
    country=scrapy.Field()
    region=scrapy.Field()
    sp_un=scrapy.Field()
    depositary=scrapy.Field()
    custodian1_or_register=scrapy.Field()
    custodian2=scrapy.Field()
    custodian3=scrapy.Field()
    structure=scrapy.Field()
    private=scrapy.Field()
    upgrade=scrapy.Field()
    successor=scrapy.Field()
    single_listed=scrapy.Field()
    effective=scrapy.Field()
    ratio_ord_adr=scrapy.Field()
    exchange=scrapy.Field()
    ticker=scrapy.Field()
    cusip=scrapy.Field()
    dr_share_isin=scrapy.Field()
    ordinary_isin=scrapy.Field()
    ordinary_sedol=scrapy.Field()
    ordinary_ticker=scrapy.Field()
    gics_industry=scrapy.Field()
    product_milestones=scrapy.Field()
    comments=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()

class CitiDistributionItem(scrapy.Item):
    company =scrapy.Field()
    date_of_notice=scrapy.Field()
    ticker=scrapy.Field()
    cusip  =scrapy.Field()
    ratio_ord_dr =scrapy.Field()
    type =scrapy.Field()
    country=scrapy.Field()
    exchange=scrapy.Field()
    record_date =scrapy.Field()
    dsf_fee=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()


class CitiDiviDistributionItem(scrapy.Item):
    company=scrapy.Field()
    record_date=scrapy.Field()
    pay_date =scrapy.Field()
    ticker=scrapy.Field()
    cusip=scrapy.Field()
    ratio_ord_dr=scrapy.Field()
    type=scrapy.Field()
    country=scrapy.Field()
    exchange =scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()

class CitiOpenCloseItem(scrapy.Item):
    company=scrapy.Field()
    ticker=scrapy.Field()
    cusip=scrapy.Field()
    country=scrapy.Field()
    exchange=scrapy.Field()
    current_status=scrapy.Field()
    closed_for=scrapy.Field()
    close_date=scrapy.Field()
    open_date=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()


class CitiCorporateItem(scrapy.Item):
    company = scrapy.Field()
    date_of_notice=scrapy.Field()
    ticker=scrapy.Field()
    cusip=scrapy.Field()
    ratio_ord_dr=scrapy.Field()
    type=scrapy.Field()
    country=scrapy.Field()
    exchange=scrapy.Field()
    corporate_action_type=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()


class CitikoreanadrDataItem(scrapy.Item):
    issuer=scrapy.Field()
    class_of_stock=scrapy.Field()
    kr_isin=scrapy.Field()
    dr_isin=scrapy.Field()
    ratio_ord_dr=scrapy.Field()
    ceiling=scrapy.Field()
    outstanding=scrapy.Field()
    available=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()

class TaiwanDataItem(scrapy.Item):
    input_date=scrapy.Field()
    market=scrapy.Field()
    company_name=scrapy.Field()
    isin_code=scrapy.Field()
    place_where_overseas_depositary_receipts_to_be_listed=scrapy.Field()
    name_of_the_depositary_institution=scrapy.Field()
    local_agent=scrapy.Field()
    total_issued_shares=scrapy.Field()
    outstanding_shares=scrapy.Field()
    total_reissuable_shares=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()

class IndiaDataItem(scrapy.Item):
    issuer=scrapy.Field()
    isin=scrapy.Field()
    ratio_share=scrapy.Field()
    head_room_drs=scrapy.Field()
    head_room_shares=scrapy.Field()
    share_reserved=scrapy.Field()
    scraped_date = scrapy.Field()
    hash=scrapy.Field()
    date=scrapy.Field()
