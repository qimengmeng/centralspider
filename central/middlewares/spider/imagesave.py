# -*- coding:utf-8 -*-


import requests

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

            else:
                image_urls = r["image_urls"]

                if len(image_urls) == 0:
                    yield r

                else:

                    top_image_url = image_urls[0]

                    config = spider.config

                    upload_url = config.get("IMAGE", "UPLOAD_URL")

                    formdata = {
                                   "image_source_url": top_image_url,
                                   "image_destination": r["image_path_base"],
                                   "thumbnail": "true",
                                   "blur": "false",
                               }
                    rep = requests.post(url=upload_url, data=formdata).json()

                    rep = eval(rep)
                    status_code = rep.get("status")
                    if int(status_code) == 200:
                        r["images"].append(rep.get("paths"))

                    yield r














