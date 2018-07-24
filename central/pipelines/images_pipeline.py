import random

import scrapy
import hashlib
from scrapy.http import Request
from scrapy.utils.python import to_bytes
from scrapy.pipelines.images import ImagesPipeline




class MyImagesPipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.images_result_field in item.fields:
            item[self.images_result_field] = [x for ok, x in results if ok]
        return item

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url, meta={'path': 'WeiboImages/%s' % item.get("account").weibo_id})

    # def file_path(self, request, response=None, info=None):
    #     if not isinstance(request, Request):
    #         url = request
    #     else:
    #         url = request.url
    #
    #     if not hasattr(self.file_key, '_base'):
    #         return self.file_key(url)
    #     elif not hasattr(self.image_key, '_base'):
    #         return self.image_key(url)
    #
    #     image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
    #     image_path = '%s/%s.jpg' % (request.meta['path'], image_guid)
    #     return image_path

    # def thumb_path(self, request, thumb_id, response=None, info=None):
    #     if not isinstance(request, Request):
    #         url = request
    #     else:
    #         url = request.url
    #     if not hasattr(self.thumb_key, '_base'):
    #         return self.thumb_key(url, thumb_id)
    #
    #     thumb_guid = hashlib.sha1(to_bytes(url)).hexdigest()
    #     thumbs_path = 'thumbs/%s/%s.jpg' % (request.meta['path'], thumb_guid)
    #     return thumbs_path