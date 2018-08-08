# -*- coding:utf-8 -*-


import requests

from central.items.basis import (
                    TweetItem,
)
from central.items.crawlmanage import (
                    SMAccountItem,
)



class ImageDownloader(object):
    """
    a spider middleware to repalce image url
    """
    def process_spider_output(self, response, result, spider):

        config = spider.config
        upload_url = config.get("IMAGE", "UPLOAD_URL")

        for obj in result:

            if isinstance(obj, (TweetItem, )):
                image_urls = obj["image_urls"]

                if len(image_urls) == 0:
                    yield obj

                else:

                    top_image_url = image_urls[0]


                    formdata = {
                                   "image_source_url": top_image_url,
                                   "image_destination": obj["image_path_base"],
                                   "thumbnail": "true",
                                   "blur": "false",
                               }
                    rep = requests.post(url=upload_url, data=formdata).json()

                    rep = eval(rep)
                    status_code = rep.get("status")
                    if int(status_code) == 200:
                        obj["images"].append(rep.get("paths"))

                    yield obj

            elif isinstance(obj, (SMAccountItem, )):
                weibo_photo = obj.get("weibo_photo")
                weibo_id = obj.get("weibo_id")

                formdata = {
                    "image_source_url": weibo_photo,
                    "image_destination": "WeiboImages/%s" % weibo_id,
                    "thumbnail": "true",
                    "blur": "false",
                }
                rep = requests.post(url=upload_url, data=formdata).json()

                rep = eval(rep)
                status_code = rep.get("status")
                if int(status_code) == 200:
                    obj["weibo_photo"] = rep.get("paths").get("images")

                    yield obj

            else:
                yield obj














