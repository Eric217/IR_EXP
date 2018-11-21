import pymysql


def get_chinese_stopwords():
    ch_stopwords_filename = './stopwords.txt'

    stop_words = []
    for line in open(ch_stopwords_filename, 'r'):
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
