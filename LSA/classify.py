
import jieba
import numpy as np
from numpy import linalg
from LSA.tools import get_chinese_stopwords, db

jieba.enable_parallel(8)  # 设置 jieba 用的 CPU 数

news_list = db.get_news_data(15)  # 测试 15 条新闻
# 目前只使用新闻内容，以后可能通过标题，或标题与内容混合
contents = []
for news in news_list:
    contents.append(news.get('content'))

stopwords = get_chinese_stopwords()

# 用于生成 词-文档，字典记录了每个词出现在哪些文档里，
dictionary = {}
curr_doc = 0

for news in contents:
    for word in jieba.lcut(news):
        if not word or word in stopwords:
            continue
        elif word in dictionary:
            dictionary[word].append(curr_doc)
        else:
            dictionary[word] = [curr_doc]

    curr_doc += 1

# 选关键词，如果需要至少在两篇或更多文章中出现过才能做关键词，就加上：
# need_appear = 2
# keywords = [k for k in dictionary.keys() if len(dictionary[k]) >= need_appear]
keywords = [k for k in dictionary.keys()]
keywords.sort()

# 将得到很大的 词-文档 稀疏矩阵 X
X = np.zeros([len(keywords), curr_doc])
for i, k in enumerate(keywords):
    for doc in dictionary[k]:
        X[i, doc] += 1

# SVD 分解
U, sigma, V = linalg.svd(X, full_matrices=True)

