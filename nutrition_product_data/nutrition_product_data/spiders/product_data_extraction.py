import scrapy
from typing import Generator
from scrapy.http import XmlResponse

class ProductDataExtraction(scrapy.Spider):

    name = 'product_extract_data'
    



    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        urls = ["https://nutritionmarket.com.au/sitemap/"]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.xpath('//h2[@class="rank-math-html-sitemap__title" and text()="Products"]//parent::*//li//a')
        for product in products:
            href = product.xpath('@href').get()
            yield scrapy.Request(url=href, callback=self.get_product, meta={'href': href})

    def get_product(self, response):
        site_map_url = response.meta.get('href')
        if response.xpath('//div[@id="tab-ingredients"]'):
            ingredients = response.xpath('//div[@id="tab-ingredients"]')
        elif response.xpath('//div[@id="tab-active-ingredients"]'):
            ingredients = response.xpath('//div[@id="tab-active-ingredients"]')
        else:
            ingredients = response.xpath('//div[@id="tab-ingredient"]')


 
        ingredient_list = ingredients.xpath('.//td[position() mod 2 = 1]')[1:]


        ingredient_data = []
        if ingredients.xpath('.//tbody'):
            for ingredient in ingredient_list:
                    # Extract the text content of the ingredient element
                if len(ingredient.xpath('.//*')) > 1:
                    for row_sub_ingredient in ingredient.xpath('.//*'):
                        row_sub_ingredient_text = row_sub_ingredient.xpath('normalize-space(.)').get()
                        ingredient_data.append(row_sub_ingredient_text)
                    joined_ingredients = ", ".join(ingredient_data)
                else:
                    ingredient_data.append(ingredient.xpath('normalize-space(.)').get())
            if len(ingredient_data) > 1:
                joined_ingredients = ", ".join(ingredient_data)
            else:
                joined_ingredients = ingredient_data[0] if len(ingredient_data) == 1 else ""

        elif len(ingredients.xpath('.//ul')) == 1:
            for list_ingredient in ingredients.xpath('.//li'):
                list_text = list_ingredient.xpath('normalize-space(.)').get()
                ingredient_data.append(list_text)
            if len(ingredient_data) > 1:
                joined_ingredients = ", ".join(ingredient_data)
            else:
                joined_ingredients = ingredient_data[0] if len(ingredient_data) == 1 else ""
        elif len(ingredients.xpath('.//ul')) >= 1:
            for list_ingredient in ingredients.xpath('.//li'):
                list_text = list_ingredient.xpath('normalize-space(.)').get()
                ingredient_data.append(list_text)
            if len(ingredient_data) > 1:
                joined_ingredients = ", ".join(ingredient_data)
            else:
                joined_ingredients = ingredient_data[0] if len(ingredient_data) == 1 else ""
        else:
            for para_ingredient in ingredients.xpath('.//p'):
                ingredient_data.append(para_ingredient.xpath('normalize-space(.)').get())
            if len(ingredient_data) > 1:
                joined_ingredients = ", ".join(ingredient_data)
            else:
                joined_ingredients = ingredient_data[0] if len(ingredient_data) == 1 else ""


        

        yield {
            'site_map': site_map_url,
            'product_name': response.css('h1.product_title.entry-title::text').get(),
            'ingredients': joined_ingredients
        }
            



        

        





