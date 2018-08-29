# -*- coding:utf-8 -*-

import requests

def upload_image_tos3(upload_url, images_post_params):

    images_info = []

    for data in images_post_params:

        rep = requests.post(url=upload_url, data=data).json()

        rep = eval(rep)
        status_code = rep.get("status")

        if int(status_code) == 200:
            images_info.append(rep.get("paths"))

    s3_images = map(lambda x: x.get("image"), images_info)
    thumb_images = map(lambda x: x.get("thumbnail"), images_info)
    tiny_images = map(lambda x: x.get("blur"), images_info)

    return (s3_images, thumb_images, tiny_images)

