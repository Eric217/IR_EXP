
import jieba
import numpy as np
import synonyms as sy
from collections import OrderedDict

import time
from numpy import linalg
from LSA.tools import get_chinese_stopwords, db, cosine

cpus = 6
news_count = 100
target_dimension = 2
use_title_only = True
min_synonyms = 0.75  # 相似度为 1 时关闭相似度功能
min_cosine = 0.75
# need_appear = 2

news_extract = 'title' if use_title_only else 'content'
jieba.enable_parallel(cpus)  # 设置 jieba 用的 CPU 数


news_list = db.get_news_data(news_count)  # 测试 15 条新闻
stopwords = get_chinese_stopwords()
dictionary = {}  # 用于生成 词-文档，字典记录了每个词出现在哪些文档里

curr_news_idx = 0
id_binding = {}
for news in news_list:
    for word in jieba.lcut(news.get(news_extract)):
        if not word or word in stopwords:
            continue
        elif word in dictionary:
            dictionary[word].append(curr_news_idx)
        else:
            dictionary[word] = [curr_news_idx]
    id_binding[curr_news_idx] = news.get('id')
    curr_news_idx += 1


# 选关键词，如果需要至少在两篇或更多文章中出现过才能做关键词，就加上：
# keywords = [k for k in dictionary.keys() if len(dictionary[k]) >= need_appear]
keywords = [k for k in dictionary.keys()]
keywords.sort()
print(keywords)

# 将得到很大的 词-文档 稀疏矩阵 X
X = np.zeros([len(keywords), len(news_list)])
for i, k in enumerate(keywords):
    for doc_id in dictionary[k]:
        X[i, doc_id] += 1

# SVD 分解
U, sigma, V = linalg.svd(X, full_matrices=True)

# 降维
Uk = U[0:, 0: target_dimension]  # 保留前 k 列
Vk = V[0: target_dimension, 0:]
sigma_k = np.diag(sigma[0: target_dimension])

keyword_count = len(keywords)
doc_count = len(news_list)

def get_doc_vectors(v_k):
    docs = []
    for i in range(doc_count):
        docs.append(v_k[0:, i])
    return docs


doc_vec = get_doc_vectors(Vk)

print('Initialize Ready...')


def get_input():
    init_query = input('输入要查询的内容')
    if not init_query:
        print('输入为空！')
        return None
    query_words = []
    for w in jieba.lcut(init_query):
        if not w or w in stopwords:
            continue
        else:
            query_words.append(w)
    if len(query_words) == 0:
        print('输入内容没有明显意义')
        return None
    return query_words


def get_fixed_keywords(query_word_list, min_match):
    """ min_match 0-1 代表接受的近义词最低匹配度, 1 代表不做近义词匹配 """
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


while True:

    query_keywords = get_input()
    if not query_keywords:
        continue
    fixed_query = get_fixed_keywords(query_keywords, min_synonyms)
    result = []
    for __i in range(len(fixed_query)):
        group = fixed_query[__i]  # 第 __i 个搜索主干
        sy_ls = []
        for _i in range(len(group)):
            word = group[_i]  # 第 _i 个近义词

            idx = -1
            for i in range(keyword_count):
                if keywords[i] == word:
                    idx = i
                    break
            if idx == -1:
                continue
            keyword_vec = Uk[idx, 0:]
            cos_ls = []
            for i in range(doc_count):
                cos = cosine(keyword_vec, doc_vec[i])
                if cos > min_cosine:
                    cos_ls.append((_i, i, cos))
            sy_ls.append(cos_ls)
        result.append(sy_ls)

    result_ls = []
    for group in result:
        result_dict = {}
        for sy_word in group:
            for cos in sy_word:
                d = cos[1]
                if d not in result_dict:
                    result_dict[d] = cos[2]
                elif result_dict[d] < cos[2]:
                    result_dict[d] = cos[2]

        result_ls.append(result_dict)

    result_dict = {}
    for group_dict in result_ls:
        for k in group_dict:
            if k not in result_dict:
                result_dict[k] = group_dict[k]
            else:
                result_dict[k] += group_dict[k]

    ok = OrderedDict(sorted(result_dict.items(), key=lambda x: x[1], reverse=True))
    r = []
    for t in ok:
        r.append(news_list[t].get('title'))

    print(r)
    time.sleep(100)

