# -*- coding:utf-8 -*-

import requests
from PIL import Image
from StringIO import StringIO


def download_buffer(url):

    resp = requests.get(url)

    return Image.open(StringIO(resp.content))
