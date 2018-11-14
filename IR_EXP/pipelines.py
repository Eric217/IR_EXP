# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class NewsPipeline(object):
    def __init__(self):
        self.file = open('data.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass


# class ImgPipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         yield scrapy.Request('http:' + item['image_url'])
#
#     def item_completed(self, results, item, info):
#
#         if not results or not results[0] or not results[0][0]:
#             raise DropItem("no image content")
#
#         item['image_path'] = results[0][1]['path']
#         return item

