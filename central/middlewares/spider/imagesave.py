# -*- coding:utf-8 -*-

import json

from scrapy import Request, FormRequest

from central.items.basis import (
                    TweetItem,
)



class ImageDownloader(object):
    """
    a spider middleware to repalce image url
    """
    def process_spider_output(self, response, result, spider):
        for r in result:
            if not isinstance(r, (TweetItem, )):
                yield r

            image_urls = r["image_urls"]

            if len(image_urls) == 0:
                yield r


            top_image_url = image_urls[0]

            config = spider.config

            upload_url = config.get("IMAGE", "UPLOAD_URL")

            yield FormRequest(
                url=upload_url,
                callback=self.parse_image,
                method='post',
                params={
                    "image_source_url": top_image_url,
                    "image_destination": r["image_path_base"],
                    "thumbnail": "true",
                    "blur": "true",
                    },
                meta={
                    "item": r,
                   }
                )

    def parse_image(self, response):

        item = response.meta.get("item")

        rep = json.loads(response.body)

        item["images"] = []
        if int(rep.get("status")) == 200:
            item["images"].append(rep.get("paths"))

        yield item








