# IR_EXP
<pre>
2018-12-04&#9;在一定的参数下，查询结果良好；数据集改变后需要相应调整部分参数，重新运行 <br>
2018-11-26&#9;可以完整运行，效果上，多个查询词的整体匹配程度计算方法需要改善 <br>
2018-11-21&#9;得到了 词-文档 矩阵，SVD <br>
2018-11-18&#9;爬虫部分已完成 <br>
2018-11-18&#9;已爬取共 5000 条左右的国内外新闻并保存在数据库中。
</pre>

## 部署与运行
### 爬虫：
确保 Crawl 文件夹下所有 py文件内的所有依赖库已安装；（py 3.6) 

确保 scrapy 已安装；  

确保 mysql 运行，并存在 database：ir_exp_db, 账号密码修改代码为本机的，存在表 News，结构为  

id int 11 unsigned auto increment primary key

time datetime

title varchar100

content varchar10000   
<br>

满足以上条件后，命令行： 

scrapy crawl NewsSpider 


### 根据LSA查询新闻的程序
确保上面的数据库存在，数据可以从 IR_EXP_DB_News.sql 中导入 

确保LSA文件夹下所有 py 文件的依赖已安装 

运行： 

python classify.py  

