import json

import jmespath
import scrapy
from scrapy.http import Request

from test_task.items import TestTaskItem


class TargetSpider(scrapy.Spider):
    name = "target"
    allowed_domains = ["https://www.target.com"]
    start_urls = []
    crawl_item_url = (
        "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?key={}&tcin={}"
        "&store_id=none&has_store_id=false&pricing_store_id={}&has_pricing_store_id=true"
        "&scheduled_delivery_store_id=none&has_scheduled_delivery_store_id=false&has_financing_options=false"
    )

    def __init__(self, url):
        self.start_urls.append(url)
        super(TargetSpider, self).__init__()

    def parse(self, response):

        tgt_data_json = self._get_tgt_data_json(response)
        apikey, tcin, pricing_store_id = self._get_params(tgt_data_json)

        crawl_url = self.crawl_item_url.format(apikey, tcin, pricing_store_id)
        yield Request(
            crawl_url,
            cb_kwargs={"tcin": tcin},
            headers={"accept": "application / json"},
            callback=self.parse_item,
            dont_filter=True,
        )

    def parse_item(self, response, tcin):
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

    def _get_tgt_data_json(self, response):
        tgt_data = response.xpath('//script[contains(text(), "window.__TGT_DATA__=")]/text()').get()
        tgt_data = tgt_data.replace("window.__TGT_DATA__= ", "").replace("undefined", "0")
        return json.loads(tgt_data)

    def _get_params(self, tgt_data_json):
        apikey = jmespath.search("__PRELOADED_QUERIES__.queries[0][0][1].apiKey", tgt_data_json)
        tcin = jmespath.search("__PRELOADED_QUERIES__.queries[0][0][1].tcin", tgt_data_json)
        pricing_store_id = jmespath.search(
            "__PRELOADED_QUERIES__.queries[0][0][1].pricing_store_id", tgt_data_json
        )
        return apikey, tcin, pricing_store_id
