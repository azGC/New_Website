# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division
import pymssql
import pandas as pd


server = "SQLDEV02\sql"
server = "127.0.0.1"
user = "dtc"
password = "asdf1234"
# 修改sql date
sql_data = "sum([2016061]) as '2016Q2', sum([2016091]) as '2016Q3', sum([2016121]) as '2016Q4',sum([2017031])as '2017Q1', sum([2017061]) as '2017Q2', sum([2017091]) as '2017Q3', sum([2017121]) as '2017Q4',sum([2018011])as '201801',sum([2018021])as '201802'"
sql_data_tech = "sum([2017031])as '2017Q1', sum([2017061]) as '2017Q2', sum([2017091]) as '2017Q3', sum([2017121]) as '2017Q4',sum([2018011])as '201801',sum([2018021])as '201802'"


# 获取品牌份额 每次修改日期
def getBrandShare(target):
    target_replace = target.replace('[', '').replace(']', '').replace('"', '')
    x_list = ['2016Q2','2016Q3','2016Q4', '2017Q1', '2017Q2', '2017Q3', '2017Q4', '201801', '201802']
    if len(target_replace) == 2:
        aim_ = "'%s'" % target_replace
    else:

        select_price = target_replace.split(',')
        aim_ = "'%s'" % select_price[0] + " and ([价格段]='"
        for i in range(1, len(select_price)):
            aim_ = aim_ + select_price[i] + '@'
        aim_ = aim_[:-1] + "')"
        aim_ = aim_.replace('@', "' or [价格段]='")

    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                SELECT top 10
                    """+sql_data+"""
                    ,[brand]
                FROM [BDCI_Phone].[dbo].[Summary_1606_1802]
                where brand != '其它' and citytier= """+aim_+"""
                group by [citytier],[brand]
                order by '201802' desc
            """
    df = pd.read_sql_query(sql, conn)
    result_ = []
    keylist = df.keys().tolist()
    for brand_index in keylist:
        scorelist = df[brand_index].tolist()
        result_.append(scorelist)

    # 行转列
    result = []
    for i in range(0, len(result_[0])):
        aim_list = []
        for i_ in range(0, len(result_)-1):
            value_ = float('%.2f' % result_[i_][i])
            aim_list.append(round(value_*100))
        result.append(aim_list)
    result.append(result_[len(result_)-1])
    result.append(x_list)
    return result

# 获取机型份额 每次修改日期
def getModelShare(target):
    # print(target)

    x_list = ['2016Q2','2016Q3','2016Q4', '2017Q1', '2017Q2', '2017Q3', '2017Q4', '201801', '201802']
    city = target[0]
    city = "'%s'" % city
    mode_ = target[2][:-1]
    model = mode_.replace(', ', '\' or name = \'')
    model = "'%s'" % model

    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                SELECT * FROM(SELECT
                   [citytier]
                  ,[2016061]
                  ,[2016091]
                  ,[2016121]
                  ,[2017031]
                  ,[2017061]
                  ,[2017091]
                  ,[2017121]
                  ,[2018011]
                  ,[2018021]
                  ,brand+' '+model as name
                FROM [BDCI_Phone].[dbo].[Summary_1606_1802])a 
                WHERE  citytier = """+city+""" and (name ="""+model+""" )
                
            """
    df = pd.read_sql_query(sql, conn)
    result_ = []
    keylist = df.keys().tolist()
    for brand_index in keylist:
        scorelist = df[brand_index].tolist()
        result_.append(scorelist)
    del result_[0]  # 删除city元素

    # 行转列
    result = []
    for i in range(0, len(result_[0])):
        aim_list = []
        for i_ in range(0, len(result_)-1):
            val = result_[i_][i]
            value_ = val * 1000000000
            value_ = round(value_)
            # value_ = float('%.7f' % result_[i_][i])
            aim_list.append(value_ / 10000000)
        result.append(aim_list)

    re_series = []
    for lab in range(len(result)):
        data_series = {'data': [], 'type': 'line', 'name': ''}
        data_series['name'] = result_[len(result_) - 1][lab]
        data_series['data'] = result[lab]
        re_series.append(data_series)
    re_result = []
    re_result.append(re_series)
    re_result.append(result_[len(result_) - 1])  # 机型名
    re_result.append(x_list)  # 添加X轴坐标
    return re_result
# getModelShare(["全国", "price_model", "苹果 iPhone 8\xa0"])

# 获取top15机型 每次修改日期
def getTop():
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                SELECT TOP 15 
                 [brand]+' '+[model] as name
                ,[2018011]
                ,[2018021]
                FROM [BDCI_Phone].[dbo].[Summary_1606_1802] 
                where citytier='全国' and brand != '其它' and model != '其它'
                order by [2018021] desc
                """
    df = pd.read_sql_query(sql, conn)
    name = df['name'].tolist()
    this_month = df['2018021'].tolist()
    last_month = df['2018011'].tolist()

    for i_list in range(0, len(this_month)):
        this_month[i_list] = float('%.4f' % this_month[i_list])
        last_month[i_list] = float('%.4f' % last_month[i_list])

    result = []
    result.append(name)
    result.append(this_month)
    result.append(last_month)

    return result
# getTop()

# 获取价格段份额 每次修改日期
def getNational(target):
    # sql_data =  "sum([2016061]) as '2016Q2', sum([2016091]) as '2016Q3', sum([2016121]) as '2016Q4',sum([2017031])as '2017Q1', sum([2017061]) as '2017Q2', sum([2017091]) as '2017Q3', sum([2017121]) as '2017Q4'"
    target_replace = target.replace('[', '').replace(']', '').replace('"', '')
    x_list = ['2016/06', '2016/09', '2016/12', '2017/03', '2017/06', '2017/09', '2017/12', '2018/01', '2018/02']

    if len(target_replace) == 2:
        aim_ = "'%s'" % target_replace
    else:
        aim_ = "'%s'" % target_replace[0:2]
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                SELECT 
                """+sql_data+"""
                ,[价格段]
                FROM [BDCI_Phone].[dbo].[Summary_1606_1802] where citytier="""+aim_+"""
                group by [价格段] 
            """
    df = pd.read_sql_query(sql, conn)
    result_ = []
    keylist = df.keys().tolist()
    for brand_index in keylist:
        scorelist = df[brand_index].tolist()
        result_.append(scorelist)
    # 行转列
    result_2 = []
    for L in range(len(result_)-1):
        r = []
        error_count = result_[L][4]/4
        r.append(error_count + result_[L][0])
        r.append(error_count + result_[L][1])
        r.append(error_count + result_[L][2])
        r.append(error_count + result_[L][3])
        result_2.append(r)
    price_name = result_[len(result_)-1]
    price_name.pop()  # 删除 null
    result_2.append(price_name)
    # 保留两位小数
    for i_list in range(0, len(result_2)-1):
        for i_ in range(0, len(result_2[i_list])):
            result_2[i_list][i_] = float('%.3f' % result_2[i_list][i_])
    # 将数据格式标准化
    # aim: [['2015/11/08',1.4,'DQ'],['2015/11/09',1,'DQ'],['2015/11/10',1,'DQ']]
    aim_data_list = []
    for price_ in range(0, 4):
        for i in range(0, len(result_2)-1):
            aim_data = []
            aim_data.append(x_list[i])
            aim_data.append(result_2[i][price_])
            aim_data.append(result_2[len(result_2) - 1][price_])
            aim_data_list.append(aim_data)
    # 价格段排序
    result = []
    order_1 = []
    order_2 = []
    order_3 = []
    order_4 = []
    for order in aim_data_list:
        if order[2] == '>3500':
            order_1.append(order)
        if order[2] == '2500-3500':
            order_2.append(order)
        if order[2] == '1500-2500':
            order_3.append(order)
        if order[2] == '<1500':
            order_4.append(order)
    result = order_1+order_2+order_3+order_4
    result = [result]+[x_list]
    return result
# getNational('"一线"')

# 获取新机份额
def getNewModel(target):
    target_ = target[1:3]
    city = "'%s'" % target_
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                SELECT 
                   [brand]+' '+[model] as name
                  ,[2018021] as share
                FROM [BDCI_Phone].[dbo].[Summary_1606_1802]
                where [citytier]="""+city+"""
                and [上市时间] Between '2018-02-01' And '2018-02-1'
            """
    df = pd.read_sql_query(sql, conn)
    name_list = df['name'].tolist()
    share_ = df['share'].tolist()
    for i in range(len(share_)):
        share_[i] = share_[i]*100
    result = []
    result.append(name_list)
    result.append(share_)
    return result
# getNewModel('全国')

def getTech(target):
    # 防止sql注入
    target = target.replace('\'', '')
    target = target.replace(' ', '')
    target = target.replace('%', '')
    if len(target) > 7:
        return ''

    sql = """
        SELECT 
        """+sql_data_tech+"""
        FROM [BDCI_Phone].[dbo].[Summary_1606_1802] where citytier='全国' and """+target+""" = '是'
    """
    conn = pymssql.connect(server, user, password, "BDCI")
    df = pd.read_sql_query(sql, conn)
    result = []
    value_ = []
    keylist = df.keys().tolist()
    for tech_index in keylist:
        scorelist = df[tech_index].tolist()
        value_.append(scorelist[0]*100)
    result.append(value_)
    result.append(keylist)
    return result
getTech("'人脸识别'")

# 获取所有机型添加select_list
def getModelList(paraList):
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                  SELECT modelname FROM (SELECT  distinct(brand+' '+model) as modelname
                  FROM [BDCI_Phone].[dbo].[Summary_1606_1802])a
                  order by modelname collate Chinese_PRC_CS_AS_KS_WS
            """
    df = pd.read_sql_query(sql, conn)
    model_list = df['modelname'].tolist()
    return model_list


