import scrapy

from IR_EXP.items import NewsItem
from selenium import webdriver

world_url = 'https://news.sina.com.cn/world/'
china_url = 'https://news.sina.com.cn/china/'


class MySpider(scrapy.Spider):
    name = "NewsSpider"
    allowed_domains = ["news.sina.com.cn"]

    start_urls = [world_url, china_url]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.browser = webdriver.Chrome()
        self.browser.set_page_load_timeout(30)

    def closed(self):
        self.browser.close()

    def parse(self, response):

        for news_url in response.xpath('//div[starts-with(@id, "subShowContent1_news")]'
                                       '/div/h2/a/@href'):
            yield scrapy.Request(url=news_url.extract(), callback=self.parse_detail)

        # 得到下一页
        # url = response.xpath("//span[@class="pagebox_next"]/text()").extract()
        # if url:
        #     next_page = "get next page" + url[0]
        #     yield scrapy.Request(next_page, callback=self.parse)
        #

    def parse_detail(self, response):
        item = NewsItem()
        item['title'] = response.xpath('//h1[@class="main-title"]/text()').extract()[0]
        ls = response.xpath('//div[@id="article"]/p').extract()
        item['content'] = '\n'.join(ls)
        return item
