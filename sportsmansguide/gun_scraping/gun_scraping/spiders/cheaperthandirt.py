import scrapy
import requests
import json

class CheaperthandirtSpider(scrapy.Spider):
    name = 'cheaperthandirt'
    
    def api_value_add(self,data):
        api_url = 'https://dev-api.gunsnation.com/api/firearm-offers'
        api_token = self.settings.get('API_KEY')
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        api_response = requests.post(api_url, json=data, headers=headers)
        if api_response.status_code==200:
            self.logger.info(f'Data append in api ---->\n{api_response.text}')
        else:
            self.logger.warning(f'Not append in api {api_response.status_code}')
            self.logger.warning(f'Not Appended Payload --->\n{data}')

    def start_requests(self):
        url="https://core.dxpapi.com/api/v1/core/?account_id=6812&domain_key=cheaperthandirt&request_id=8822571711618&_br_uid_2=uid%3D7371636741447%3Av%3D15.0%3Ats%3D1721053754855%3Ahc%3D2&ref_url=https%3A%2F%2Fwww.cheaperthandirt.com%2Ffirearms%2F&url=https%3A%2F%2Fwww.cheaperthandirt.com%2Ffirearms%2F&auth_key=gv1imc0tfszwhmze&request_type=search&search_type=category&fl=pid%2Ctitle%2Cbrand%2Cprice%2Csale_price%2Cthumb_image%2Csku_thumb_images%2Csku_swatch_images%2Csku_color_group%2Curl%2Cprice_range%2Csale_price_range%2Cdescription%2Cbc_storefront_id%2CaverageRating%2Csku%2CFC-code&rows=18&start=0&q=10703&facet.range=price&stats.field=price"
        yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        data=json.loads(response.text)
        total_count=data['response']['numFound']
        for offset in range(0,total_count+18,18):
            url=f"https://core.dxpapi.com/api/v1/core/?account_id=6812&domain_key=cheaperthandirt&request_id=8822571711618&_br_uid_2=uid%3D7371636741447%3Av%3D15.0%3Ats%3D1721053754855%3Ahc%3D2&ref_url=https%3A%2F%2Fwww.cheaperthandirt.com%2Ffirearms%2F&url=https%3A%2F%2Fwww.cheaperthandirt.com%2Ffirearms%2F&auth_key=gv1imc0tfszwhmze&request_type=search&search_type=category&fl=pid%2Ctitle%2Cbrand%2Cprice%2Csale_price%2Cthumb_image%2Csku_thumb_images%2Csku_swatch_images%2Csku_color_group%2Curl%2Cprice_range%2Csale_price_range%2Cdescription%2Cbc_storefront_id%2CaverageRating%2Csku%2CFC-code&rows=18&start={offset}&q=10703&facet.range=price&stats.field=price"
            yield scrapy.Request(url,callback=self.parse_items,dont_filter=True)

    def parse_items(self,response):
        data=json.loads(response.text)
        for item in data['response']['docs']:
            items={}
            items["offer_url"]=item.get('url','')
            items['vendor_url']="https://www.cheaperthandirt.com/"
            items['upc']=item.get('url').split('/')[-1].replace('.html','').replace('FC-','')
            items['price']=float(item['sale_price'])
            if items['upc'] and items['price']:
                yield {'data':items}
                data = {
                    "data": items
                }
                self.api_value_add(data)
            else:
                data={
                    "data": items
                }
                self.logger.warning(f'Mandatory Fields are Missing -----> \n{data}')
