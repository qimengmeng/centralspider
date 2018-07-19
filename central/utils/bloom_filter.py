# -*- coding: utf-8 -*-
import redis


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    ###########
    # 初始化
    # host、port、db：redis参数
    # conn：redis连接
    # bit_size：过滤器长度
    # seeds：随机数种子
    # hash_funcs：哈希函数集
    # key：过滤器
    def __init__(self, host, port, db):

        self.conn = redis.Redis(host=host,
                                port=port,
                                db=db)
        self.bit_size = 1 << 32
        self.seeds = [5, 7, 11, 13, 23, 31, 37, 47, 53, 61]
        self.hash_funcs = [SimpleHash(self.bit_size, seed) for seed in self.seeds]
        self.key = 'scrapy_filter'

    ###########
    # 插入数据
    # key：过滤器
    # url：内容
    def insert(self, url):
        for func in self.hash_funcs:
            loc = func.hash(url)
            self.conn.setbit(self.key, loc, 1)

    ###########
    # 清空过滤器
    def delete(self):
        self.conn.delete(self.key)

    ###########
    # 检查数据
    # url：数据
    def check(self, url):
        ret = True
        for func in self.hash_funcs:
            loc = func.hash(url)
            ret = ret & self.conn.getbit(self.key, loc)
        return ret

    ###########
    # 在过滤器中检查数据并更新
    # url：数据
    def check_and_update(self, url):
        check_result = self.check(url)
        if not check_result:
            self.insert(url)
            return False
        else:
            return True


if __name__ == '__main__':
    filter_ = BloomFilter()
    filter_.delete()
