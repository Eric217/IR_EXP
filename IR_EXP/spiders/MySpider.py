import scrapy
import time

from scrapy.http import HtmlResponse
from datetime import datetime
from selenium import webdriver

from IR_EXP.items import NewsItem


world_url = 'https://news.sina.com.cn/world/'
china_url = 'https://news.sina.com.cn/china/'


class MySpider(scrapy.Spider):
    name = "NewsSpider"
    allowed_domains = ["news.sina.com.cn"]

    # 因为国内新闻和国际新闻的网页结构不一样，所以下面的 start_url 注释里有相应的 XPath
    start_urls = [world_url]  # [china_url]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.curr_page = 1
        self.browser = webdriver.Chrome()
        self.browser.set_page_load_timeout(30)

        # 这个属性是为了查询分页时候传 request 参数，在 middleware 中赋值
        self.special_request = None

    def parse(self, response):

        # 对于每一个新闻的 url，进行二级 parse
        for news_url in response.xpath('//div[starts-with(@id, "subShowContent1_news")]'
                                       '/div/h2/a/@href'):
            # 国内：xpath('//div[@class="feed-card-item"]/h2/a/@href')
            yield scrapy.Request(url=news_url.extract(), callback=self.parse_detail,
                                 flags=[1])
            # 上面 flags 参数仅仅是为了在 middleware 中区别 parse detail

        # 第一页结束，得到翻页按钮
        next_p = self.browser.find_element_by_xpath(
            '//span[@class="pagebox_next"]/a[@title="下一页"]')
        # 国内：xpath('//span[@class="pagebox_next"]/a')

        if next_p:
            try:
                # 一页大约 20 条，爬多少页在这里限制
                if self.curr_page == 200:
                    return

                # 模拟点击分页，然后下拉加载
                next_p.click()
                time.sleep(3)

                for i in range(0, 3):
                    self.browser.execute_script(
                        'window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(1.6)

                self.curr_page += 1

                # 这里有一个坑，parse 函数不可以返回 generator，因此这里循环 yield；
                # 由于网页的下一页按钮是绑定的 js 函数，因此需要用 web driver 模拟点击
                # 而构造 Response，request 参数是必需的，在 middleware 中保持引用即可
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

    # 新闻详情页进行二级解析，创建并格式化 item
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
