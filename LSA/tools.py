import pymysql
import math
import codecs
import unicodedata
import jieba
import synonyms as sy


def get_tf_dict(data_list, stop_words, extract):
    """
    用于生成 词-文档，字典记录了每个词出现在哪些文档里
    :param data_list: [{'id': 1, }, {}, ]
    :param stop_words: 停用词列表
    :param extract: news 对象取的 key
    :return: {word1: [doc1, doc1, doc2, doc3], }
    """
    tf_dict = {}

    curr_news_idx = 0
    # id_binding = {}
    for news in data_list:
        for word in jieba.lcut(news.get(extract)):
            if not word:
                continue
            w1 = word.strip()
            if not word or not w1 or is_number(w1) or w1 in stop_words:
                continue
            elif word in tf_dict:
                tf_dict[word].append(curr_news_idx)
            else:
                tf_dict[word] = [curr_news_idx]
        # id_binding[curr_news_idx] = news.get('id')
        curr_news_idx += 1

    return tf_dict


def get_input(stop_words):
    """
    获取用户输入，对用户查询分词、去停用词，返回处理后的查询词列表

    :param stop_words: 停用词列表
    :return: 字符串列表
    """
    init_query = input('\n输入要查询的内容：')
    if not init_query:
        print('输入为空！')
        return []
    query_words = []
    for w in jieba.lcut(init_query):
        if not w or w in stop_words:
            continue
        else:
            query_words.append(w)
    if len(query_words) == 0:
        print('输入内容没有明显意义')
        return []
    return query_words


def get_fixed_keywords(query_word_list, min_match):
    """
    对查询词列表中的每一个词，找其近义词列表，最终返回总列表
    :param query_word_list: 查询词字符串列表
    :param min_match: 近义词程度，0-1，1 代表不找近义词
    :return: [[str, str], []]
    """
    if min_match < 0.5:
        min_match = 0.5
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
    def get_news_data(self, count):
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
