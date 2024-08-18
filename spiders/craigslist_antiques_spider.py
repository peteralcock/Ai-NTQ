import scrapy
import json
from scrapy.http import FormRequest

class CraigslistAntiquesSpider(scrapy.Spider):
    name = "craigslist_antiques"
    allowed_domains = ["craigslist.org"]
    start_urls = ["https://craigslist.org/search/ata"]

    def parse(self, response):
        # Extracting the links to individual listings
        listings = response.css('a.result-title::attr(href)').getall()
        for listing in listings:
            yield scrapy.Request(url=listing, callback=self.parse_listing)

    def parse_listing(self, response):
        # Extracting information about the antique
        title = response.css('span#titletextonly::text').get()
        price = response.css('span.price::text').get()
        description = response.css('section#postingbody').get()

        # Creating a dictionary to store the extracted data
        item = {
            'title': title,
            'price': price,
            'description': description,
            'url': response.url
        }

        # Call OpenAI API to assess market value
        yield FormRequest(
            url='https://api.openai.com/v1/completions',
            method='POST',
            headers={
                'Authorization': f'Bearer YOUR_OPENAI_API_KEY',
                'Content-Type': 'application/json',
            },
            body=json.dumps({
                "model": "text-davinci-003",
                "prompt": f"Analyze the following Craigslist antique description and estimate its market value: \n\n{description}",
                "max_tokens": 50
            }),
            meta={'item': item},
            callback=self.parse_openai_response
        )

    def parse_openai_response(self, response):
        item = response.meta['item']
        result = json.loads(response.body)
        estimated_value = result['choices'][0]['text'].strip()

        # Add the estimated value to the item
        item['estimated_value'] = estimated_value

        yield item
