import numpy as np

from collections import OrderedDict
from numpy import linalg
from LSA.tools import *


# 300文章，14000 左右关键词，29维，全文检索，cos值 0.82
# 2000文章，7300 左右关键词，144维，仅标题检索，cos值 0.85


def extract(obj):
    return obj.get('title')


def target_dim(data_list):
    d = len(data_list) // 10
    if d == 1 or d == 2:
        d = 3
    elif d == 0:
        d = len(data_list)
    return d


def initialize():
    stop_list = get_chinese_stopwords()

    news_list = db.get_news_data(500)

    # 生成 词-文档 字典记录了每个词出现在哪些文档里
    tf_dict = {}
    curr_news_idx = 0
    for news in news_list:
        for word in jieba.lcut(extract(news)):
            if not word:
                continue
            w1 = word.strip()
            if not word or not w1 or is_number(w1) or w1 in stop_list:
                continue
            elif word in tf_dict:
                tf_dict[word].append(curr_news_idx)
            else:
                tf_dict[word] = [curr_news_idx]
        curr_news_idx += 1

    key_words = [k for k in tf_dict.keys()]

    # 得到很大的 词-文档 稀疏矩阵 X
    X = np.zeros([len(key_words), len(news_list)])
    for l, k in enumerate(key_words):
        for doc_id in tf_dict[k]:
            X[l, doc_id] += 1

    # SVD 分解
    U, sigma, V = linalg.svd(X, full_matrices=True)

    # 降维
    target_dimension = target_dim(news_list)
    Uk = U[0:, 0: target_dimension]
    Vk = V[0: target_dimension, 0:]
    # print('降至维数:\t\t\t', target_dimension)

    # 文档向量列表，一会直接 for in 计算
    news_vectors = []
    for l in range(len(news_list)):
        news_vectors.append(Vk[0:, l])

    return stop_list, key_words, news_list, Uk, news_vectors


def recommend(origin_query_ls, stop_word_ls, keyword_ls, u_k, article_ls, article_vec_ls):

    query = ''
    for q in origin_query_ls:
        query += q

    fixed_query = get_fixed_query(query, stop_word_ls)
    print('查询：', fixed_query)

    if not fixed_query:
        return None

    group_ls = []
    for group in fixed_query:
        # 第 __i 个搜索主干（近义词列表）
        sy_ls = []
        for word in group:
            # 第 _i 个近义词
            idx = -1
            for i in range(len(keyword_ls)):
                if keyword_ls[i] == word:
                    idx = i
                    break
            if idx == -1:
                continue
            keyword_vec = u_k[idx, 0:]
            cos_ls = []
            for i in range(len(article_ls)):
                cos = cosine(keyword_vec, article_vec_ls[i])
                if cos and cos > 0.85:
                    # 找到一个合格的词，(以后可能扩展用到 word)，i代表匹配的文章，cos 为余弦值
                    cos_ls.append((word, i, cos))
            sy_ls.append(cos_ls)
        group_ls.append(sy_ls)

    group_dict_ls = []
    for group in group_ls:
        group_part_dict = {}
        for sy_word in group:
            for cos in sy_word:
                d = cos[1]
                if d not in group_part_dict:
                    group_part_dict[d] = cos
                elif group_part_dict[d][2] < cos[2]:
                    group_part_dict[d] = cos

        group_dict_ls.append(group_part_dict)

    result_dict = {}
    for group_dict in group_dict_ls:
        for k in group_dict:
            cos = group_dict[k]
            if k not in result_dict:
                result_dict[k] = [cos[2], [cos[0]]]
            else:
                result_dict[k][0] = result_dict[k][0] + cos[2]
                result_dict[k][1].append(cos[0])
    # print(result_dict)

    # noinspection PyTypeChecker
    final_dict = OrderedDict(
        sorted(result_dict.items(), key=lambda t: t[1][0], reverse=True))

    result_ls = []

    for k in final_dict:
        result_ls.append((article_ls[k].get('id'), final_dict[k][1], extract(article_ls[k])))

    return result_ls


stopwords, keywords, articles, _u_k, article_vec = initialize()


if True:  # 请求时

    q_list = ["加州火山死亡的人数"]
    re = recommend(q_list, stopwords, keywords, _u_k, articles, article_vec)

    for i in re:
        print(i)

    # TODO: -
    # 与查询相关性高的结果 re 可能只含几个很少（假设目的要返回20条）：
    # 解决1、随机从原始列表里抽取几个补足；
    # 解决2、降低相关性要求，即 cos 值
    # re 结果很多时，取出前20即可
