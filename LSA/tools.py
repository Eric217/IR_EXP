import pymysql
import math
import codecs
import unicodedata
import jieba


jieba.enable_parallel(4)


def get_fixed_query(origin_query, stop_list):
    """

    :param stop_list: 停用词表
    :param origin_query: 查询串
    :return: 修正后的查询，格式：
    """

    if len(origin_query) == 0:
        # print('输入为空')
        return None
    query_words = []
    for w in jieba.lcut(origin_query):
        if not w or w in stop_list:
            continue
        else:
            query_words.append(w)
    if len(query_words) == 0:
        # print('输入内容没有明显意义')
        return None
    query_words = list(set(query_words))
    fixed_qry = get_fixed_keywords(query_words)

    return fixed_qry


def get_fixed_keywords(query_word_list, min_match=1):
    """
    对查询词列表中的每一个词，找其近义词列表，最终返回总列表

    :param query_word_list: 查询词 列表
    :param min_match: 近义词程度，0-1，1 代表不找近义词，取值取决于近义词库
    :return: [[str, str], []] or None
    """
    if len(query_word_list) == 0:
        return None
    if min_match < 0.5:
        min_match = 0.5
    if min_match < 1:
        import synonyms as sy
    # 可接受的最小近义词相似度，1 代表禁用近义词, 一般不用变
    # min_synonyms = 0.77
    fixed = []
    for w in query_word_list:
        r = []
        if min_match < 1:
            sy_words, sy_scores = sy.nearby(w)
            for i in range(len(sy_words)):
                if sy_scores[i] > min_match:
                    r.append(sy_words[i])
        if w not in r:
            r.insert(0, w)
        fixed.append(r)
    return fixed


def cosine(a, b):
    if len(a) != len(b):
        print('error: cos length')
        return None
    part_up = 0.0
    a_sq = 0.0
    b_sq = 0.0
    for a1, b1 in zip(a,b):
        part_up += a1*b1
        a_sq += a1**2
        b_sq += b1**2
    part_down = math.sqrt(a_sq*b_sq)
    if part_down == 0.0:
        return None
    else:
        return part_up / part_down


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def get_chinese_stopwords():
    ch_stopwords_filename = './stopwords.txt'

    stop_words = []
    for line in codecs.open(ch_stopwords_filename, 'r', 'utf-8'):
        w = line.replace('\n', '')
        if w:
            stop_words.append(w)
    return stop_words


class DataBase(object):

    query_text = "select * from News"
    query_text += ' limit '

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

    # count 为需要返回的数目，-1 表示全部
    def get_news_data(self, count=-1):
        if count == -1:
            count = 1000000
        query = self.query_text + pymysql.escape_string(str(count))
        return self.fetch_data(query)

    def get_sample_data(self, count):
        """
        与 get_news_data 唯一的区别是，这里取的数据是从第一条开始的（方便看着数据库测试）

        :param count:
        :return:
        """
        query = "select * from News where id < " + pymysql.escape_string(str(580+count))
        return self.fetch_data(query)

    def fetch_data(self, final_query):
        self.cursor.execute(final_query)
        results = self.cursor.fetchall()
        data = []
        for row in results:
            news = {'id': row[0], 'time': row[1], 'title': row[2], 'content': row[
                3].replace('原标题', '')}
            data.append(news)
        return data

    def __del__(self):
        self.cursor.close()
        self.connect.close()


db = DataBase()
