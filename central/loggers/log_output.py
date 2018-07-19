# -*- coding: utf-8 -*-
import json
import datetime
from kafka.errors import KafkaError


###########
# 日志类
class Logout(object):
    ###########
    # 初始化
    # 测试时log_type=test,默认
    # 生产时log_type=product
    def __init__(self, log_type='test', producer=None, diff=0):

        self.log_type = log_type

        self.producer = producer

        self.diff = diff

    ###########
    # 记录日志
    def logging(self, website, message, level='DEBUG'):
        # 生产环境，发送至kafka
        if self.log_type == 'product':
            now = (datetime.datetime.now() + datetime.timedelta(hours=int(self.diff)))\
                .strftime('%Y-%m-%dT%H:%M:%S.000Z')
            # 封装数据
            params = {'level': level,
                      'time': now,
                      'message': message,
                      'website': website}
            # 转化为json
            message = json.dumps(params).encode('utf-8')
            # 发送至kafka
            try:
                self.producer.send('crawler_error', str(message))
                self.producer.flush()
            except KafkaError as e:
                print e
        # 测试环境，发送至控制台
        else:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print now + ' [developer] ' + level + ': ' + message + ' ' + website
