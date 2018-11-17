import scrapy
import time

from scrapy.http import HtmlResponse
from datetime import datetime

from IR_EXP.items import NewsItem
from selenium import webdriver

world_url = 'https://news.sina.com.cn/world/'
china_url = 'https://news.sina.com.cn/china/'


class MySpider(scrapy.Spider):
    name = "NewsSpider"
    allowed_domains = ["news.sina.com.cn"]

    start_urls = [world_url]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.curr_page = 1
        self.browser = webdriver.Chrome()
        self.browser.set_page_load_timeout(30)
        self.special_request = None

    def parse(self, response):

        for news_url in response.xpath('//div[starts-with(@id, "subShowContent1_news")]'
                                       '/div/h2/a/@href'):
            yield scrapy.Request(url=news_url.extract(), callback=self.parse_detail,
                                 flags=[1])  # flag 是为了在 middleware 中区别 parse detail

        next_p = self.browser.find_element_by_xpath(
            '//span[@class="pagebox_next"]/a[@title="下一页"]')

        if next_p:
            try:
                if self.curr_page == 75:  # 爬 5000多条算了
                    return
                next_p.click()
                time.sleep(3)
                for i in range(0, 3):
                    self.browser.execute_script(
                        'window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(1.6)

                self.curr_page += 1
                for r in self.parse(HtmlResponse(body=self.browser.page_source,
                                                 encoding='utf-8',
                                                 url=self.browser.current_url,
                                                 request=self.special_request)):
                    yield r
            except Exception:
                print('------ next page timeout or error ------', self.curr_page)
                self.browser.execute_script('window.stop()')
        else:
            print('------ no more next page ------', self.curr_page)

    @staticmethod
    def parse_detail(response):
        item = NewsItem()
        ls = response.xpath('//div[@id="article"]'
                            '/p[not(contains(@class, "show_author"))]/text()').extract()
        if len(ls) <= 1:
            item['title'] = ''
            return item

        item['content'] = '\n'.join(ls)
        item['title'] = response.xpath('//h1[@class="main-title"]/text()').extract()[0]

        time_str = response.xpath('//span[@class="date"]/text()')[0].extract()

        item['time'] = datetime.strptime(time_str, '%Y年%m月%d日 %H:%M').strftime(
            "%Y-%m-%d %H:%M:%S")

        return item
