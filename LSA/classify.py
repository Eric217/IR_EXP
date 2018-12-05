import numpy as np

from collections import OrderedDict
from numpy import linalg
from LSA.tools import *

# configurations ----------
# 测试配置
# 300文章，14000 左右关键词，29维，全文检索，cos值 0.82
# 2000文章，7300 左右关键词，144维，仅标题检索，cos值 0.85

# 选取多少条数据做数据集
news_count = 300

# 降维到具体维数
target_dimension = 29

# 只使用标题检索(True) 或者全文检索(False)
use_title_only = False

# 可接受的最小近义词相似度，1 代表禁用近义词, 一般不用变
min_synonyms = 0.77

# 可接受的最小 词-文档 向量余弦
min_cosine = 0.82

# jieba 使用的 CPU 核心数
cpus = 6

# Initialization ----------

jieba.enable_parallel(cpus)

news_list = db.get_sample_data(news_count)

stopwords = get_chinese_stopwords()

# 用于生成 词-文档，字典记录了每个词出现在哪些文档里
dictionary = get_tf_dict(news_list, stopwords, 'title' if use_title_only else 'content')

# print(dictionary)

keywords = [k for k in dictionary.keys()]

# 得到很大的 词-文档 稀疏矩阵 X
X = np.zeros([len(keywords), len(news_list)])
for i, k in enumerate(keywords):
    for doc_id in dictionary[k]:
        X[i, doc_id] += 1

# SVD 分解
U, sigma, V = linalg.svd(X, full_matrices=True)

# 降维 保留前 k 列
Uk = U[0:, 0: target_dimension]
Vk = V[0: target_dimension, 0:]
sigma_k = np.diag(sigma[0: target_dimension])
print('运行配置：\n\t' + (
      '仅标题检索' if use_title_only else '全文检索'), '\n\t' +
      '文章数:\t\t\t\t', Vk.shape[1], "\n\t" +
      '关键词数:\t\t\t', Uk.shape[0], '\n\t' +
      '降至维数:\t\t\t', target_dimension, '\n\t' +
      '最小近义词相似度:\t\t', min_synonyms, '\n\t' +
      '文档与词向量最小余弦:\t', min_cosine)

# 文档向量列表，一会直接 for in 计算
news_vectors = []
for i in range(len(news_list)):
    news_vectors.append(Vk[0:, i])

print('\n初始化完成')

while True:

    query_keywords = get_input(stopwords)
    if len(query_keywords) == 0:
        continue
    fixed_query = get_fixed_keywords(query_keywords, min_synonyms)
    print('修正后的查询：', fixed_query)

    group_ls = []
    for group in fixed_query:
        # 第 __i 个搜索主干（近义词列表）
        sy_ls = []
        for word in group:
            # 第 _i 个近义词
            idx = -1
            for i in range(len(keywords)):
                if keywords[i] == word:
                    idx = i
                    break
            if idx == -1:
                continue
            keyword_vec = Uk[idx, 0:]
            cos_ls = []
            for i in range(len(news_list)):
                cos = cosine(keyword_vec, news_vectors[i])
                if cos and cos > min_cosine:
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

    print("结果如下，已按照相关度排序：")

    # 这里有排序后的文章 id，可以直接查询数据库，扩展其他功能
    for k in final_dict:
        print(str(news_list[k].get('id')) + ':',
              final_dict[k][1],
              news_list[k].get('title'))
