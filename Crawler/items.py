# -*- coding: utf-8 -*-

import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
