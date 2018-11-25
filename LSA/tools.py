import pymysql
import math
import codecs

def cosine(a, b):
    if len(a) != len(b):
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
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        data = []
        for row in results:
            news = {'id': row[0], 'time': row[1], 'title': row[2], 'content': row[3]}
            data.append(news)
        return data

    def __del__(self):
        self.cursor.close()
        self.connect.close()


db = DataBase()
