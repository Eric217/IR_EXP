# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem

import pymysql


class NewsPipeline(object):

    # 插入语句
    sql_insert = '''insert into News(time, title, content) 
                      values('{time}', '{title}','{content}')'''

    def __init__(self):

        self.connect = pymysql.connect(
            host='localhost',
            port=3306,
            db='ir_exp_db',
            user='eric',
            passwd='0202',
            charset='utf8',
            use_unicode=True
        )

        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    # noinspection PyUnusedLocal
    def process_item(self, item, spider):
        # 对于内容只有图片的新闻，我们暂不做处理，丢弃
        if len(item['title']) == 0:
            raise DropItem('----- Image News, Drop -----')

        sql_text = self.sql_insert.format(
            time=pymysql.escape_string(item['time']),
            title=pymysql.escape_string(item['title']),
            content=pymysql.escape_string(item['content'])
        )
        # 插入数据库
        self.cursor.execute(sql_text)
        return item

    def open_spider(self, spider):
        pass

    # noinspection PyUnusedLocal
    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
