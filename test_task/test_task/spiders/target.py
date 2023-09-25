import json
import re

import jmespath
import scrapy
from scrapy.http import Request
from w3lib.url import url_query_parameter

from test_task.items import TestTaskItem


class TargetSpider(scrapy.Spider):
    name = "target"
    allowed_domains = ["https://www.target.com"]
    start_urls = []
    crawl_item_url = (
        "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?"
        "key=9f36aeafbe60771e321a7cc95a78140772ab3e96&tcin={}&is_bot=false"
        "&store_id=1771&pricing_store_id=1771&has_pricing_store_id=true&has_financing_options=true"
        "&has_size_context=true&skip_personalized=true"
        "&skip_variation_hierarchy=true&channel=WEB&page=%2Fp%2Fundefined"
    )

    def __init__(self, url):
        self.start_urls.append(url)
        super(TargetSpider, self).__init__()

    def parse(self, response, *args, **kwargs):

        tcin_from_url = self._tcin_from_url(response)

        crawl_url = self.crawl_item_url.format(tcin_from_url)
        yield Request(
            crawl_url,
            headers={"accept": "application/json"},
            callback=self.parse_item,
            meta={'handle_httpstatus_list': [404]},
            dont_filter=True,
        )

    def parse_item(self, response):
        item = TestTaskItem()

        json_data = json.loads(response.body.decode())
        item["price"] = jmespath.search("data.product.price.formatted_current_price", json_data)
        item["description"] = jmespath.search(
            "data.product.item.product_description.downstream_description", json_data
        )
        item["images"] = jmespath.search(
            "data.product.item.enrichment.images.content_labels[].image_url", json_data
        )
        item["title"] = jmespath.search("data.product.item.product_description.title", json_data)

        return item

    def _tcin_from_url(self, response):
        preselected_tcin = url_query_parameter(response.url, 'preselect')
        found = re.search(r'A-(\d+)', response.url)
        if preselected_tcin or found:
            return preselected_tcin or found.group(1)
