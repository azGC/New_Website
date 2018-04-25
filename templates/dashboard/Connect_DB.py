# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division
import pymssql
import pandas as pd
import urllib

server = "SQLDEV02\sql"
server = "127.0.0.1"
user = "dtc"
password = "asdf1234"
sql_data = "sum([2016061]) as '2016Q2', sum([2016091]) as '2016Q3', sum([2016121]) as '2016Q4',sum([2017031])as '2017Q1', sum([2017061]) as '2017Q2', sum([2017091]) as '2017Q3', sum([2017121]) as '2017Q4',sum([2018011])as '201801',sum([2018021])as '201802'"

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
                    sum([2016061]) as '2016Q2', sum([2016091]) as '2016Q3', sum([2016121]) as '2016Q4',sum([2017031])as '2017Q1', sum([2017061]) as '2017Q2', sum([2017091]) as '2017Q3', sum([2017121]) as '2017Q4',sum([2018011])as '201801',sum([2018021])as '201802'
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


# 获取全国份额
def getNational(target):
    target_replace = target.replace('[', '').replace(']', '').replace('"', '')
    x_list = ['2016/02', '2016/03', '2016/04', '2017/01', '2017/02', '2017/03', '2017/04', '2018/01', '2018/02']

    if len(target_replace) == 2:
        aim_ = "'%s'" % target_replace
    else:
        aim_ = "'%s'" % target_replace[0:2]
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                SELECT 
                sum([2016061]) as '2016Q2', sum([2016091]) as '2016Q3', sum([2016121]) as '2016Q4',sum([2017031])as '2017Q1', sum([2017061]) as '2017Q2', sum([2017091]) as '2017Q3', sum([2017121]) as '2017Q4',sum([2018011])as '201801',sum([2018021])as '201802'
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
getNational('"一线"')



# 获取所有机型添加select_list
def getModel(paraList):
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
                  SELECT modelname FROM (SELECT  distinct(brand+' '+model) as modelname
                  FROM [BDCI_Phone].[dbo].[Summary_1606_1802])a
                  order by modelname collate Chinese_PRC_CS_AS_KS_WS
            """
    df = pd.read_sql_query(sql, conn)
    model_list = df['modelname'].tolist()
    return model_list


def getLevel2Attributes(paraList):
    list1 = paraList.strip('[]')
    list2 = list1.replace('"','')
    list3 = list2.split(',')
    conn = pymssql.connect(server, user, password, "BDCI")
    sql = """
            USE BDCI
            SELECT  
                 Brand
                ,Dimension
                ,keyindex
                ,KeyModifier
                ,SentenceAttitude
                ,case when SentenceAttitude >= 1 then '1'
            WHEN 
                SentenceAttitude = 0 then '0'
            WHEN
                SentenceAttitude <= -1 then '-1' end  
            AS
                 Attitude
                ,frequency
            FROM 
                DM_AutoHome_WOM_SecondLevelIndex_Noun_Modifier_Attitude_Frequency
            WHERE 
                updateflag=0 and keyindex!='老板键' 
            ORDER BY 
                keyindex desc 
            """
    df = pd.read_sql_query(sql, conn)
    #brand = u'帕萨特'
    #dimension = u'操控'
    brand = list3[0]
    dimension = list3[1]
    df = df.loc[df['Brand'] == brand]
    df = df.loc[df['Dimension'] == dimension]
    indexList = df['keyindex'].tolist()
    indexList_de_weight = list(set(indexList))  # 列表去重（乱序）
    indexList_de_weight.sort(key=indexList.index)  # 恢复列表次序
    indexList = indexList_de_weight
    result = []
    title = ['index', '满意', '没感觉', '不满意']
    result.append(title)
    for index in indexList:
        manyiCount = 0
        meiganjueCount = 0
        bumanyiCount = 0
        sum_list = []
        attitudeList = df.loc[df['keyindex'] == index]['Attitude'].tolist()
        for attitude in attitudeList:
            if attitude == '1':
                manyiCount += 1
            elif attitude == '0':
                meiganjueCount += 1
            else:
                bumanyiCount += 1
        subResult = [index, manyiCount, meiganjueCount, bumanyiCount]
        result.append(subResult)
    result_return = result[0:10]
    # 返回值排序
    for key in range(1, len(result_return)):
        sum_ = result_return[key][1]+result_return[key][2]+result_return[key][3]
        sum_list.append(sum_)

    dit_order = dict(zip(indexList[:10], sum_list))
    dit_order = sorted(dit_order.items(), key=lambda d: d[1])
    order_list = []
    for tup in dit_order:
        order_list.append(tup[0])  # 得到list顺序
    # result_return = sorted(result_return[1:], key=order_list.index)
    retuen_list_ = []
    retuen_list = []
    for key in range(0, len(order_list)):
        for value in result_return:
            if order_list[key] == value[0]:
                retuen_list_=[order_list[key]]
                retuen_list_.append(value[1])
                retuen_list_.append(value[2])
                retuen_list_.append(value[3])
                retuen_list.append(retuen_list_)
    retuen_list = [title] + retuen_list
    return retuen_list
getLevel2Attributes("凯美瑞,空间")

# 车系选择框列表
def Config_get_company(id_):
    id_ = int(id_)  # 防止SQL注入

    sql = """
            SELECT 
                 [SERIE_ID]
                ,[SERIE_NAME_CN]
                ,[COMPANY_ID]
                ,[COMPANY_NAME_CN]
            FROM 
                [BDCI_CHEXUN].[stg].[CONFIG_KEY_2018_01_30] 
            WHERE
                BRAND_ID="""+str(id_)+"""
            """
    conn = pymssql.connect(server, user, password, "BDCI")
    df = pd.read_sql_query(sql, conn)

    re_list = [] # 返回列表

    company_dic = {
        "companyId": "",
        "companyName": "",
        "seriesList": []
    } # 第一层嵌套 公司
    series_dic = {
        "seriesId": "",
        "seriesName": ""
    } # 第二次嵌套 车系

    SERIE_ID = df['SERIE_ID'].tolist()
    SERIE_NAME = df['SERIE_NAME_CN'].tolist()
    COMPANY_ID = df['COMPANY_ID'].tolist()
    COMPANY_NAME_CN = df['COMPANY_NAME_CN'].tolist()

    dic_serie = dict(zip(SERIE_ID, SERIE_NAME))
    dic_company = dict(zip(COMPANY_ID, COMPANY_NAME_CN))
    dic_key_id = dict(zip(SERIE_ID, COMPANY_ID))
    for company_id in dic_company.keys():
        company_dic = {
            "companyId": "",
            "companyName": "",
            "seriesList": []
        }
        company_dic["companyId"] = company_id
        company_dic["companyName"] = dic_company[company_id]
        for series_id in SERIE_ID:
            if company_id == dic_key_id[series_id]:
                # print(company_id, dic_key_id[series_id], series_id)
                series_dic = {
                    "seriesId": "",
                    "seriesName": ""
                }
                series_dic["seriesId"] = series_id
                series_dic["seriesName"] = dic_serie[series_id]
                company_dic["seriesList"].append(series_dic)
        re_list.append(company_dic)
    return re_list

# Config_get_company(23)

# 车型选择框
def Config_get_model(id_):
    id_ = int(id_)  # 防止SQL注入

    sql = """  
            SELECT 
                 车型名称
                ,年代款
                ,SPEC_ID
            FROM 
                [BDCI_CHEXUN].[stg].[CONFIG_KEY_SERIE_SPEC] 
            WHERE 
                [车型名称] 
            IN( 
                SELECT 
                [车型名称]
                FROM 
                [BDCI_CHEXUN].[stg].[CONFIG_KEY_SERIE_SPEC] 
                GROUP BY 
                [车型名称] having count([车型名称]) = 1 )
            AND
                SERIE_ID=""" + str(id_) + """
            GROUP BY 年代款,车型名称,SPEC_ID
            """
    conn = pymssql.connect(server, user, password, "BDCI")
    df = pd.read_sql_query(sql, conn)

    re_list = []  # 返回列表

    year_dic = {
        "yearId": "",
        "yearName": "",
        "modelList": []
    }  # 第一层嵌套 年份
    model_dic = {
        "modelId": "",
        "modelName": ""
    }  # 第二次嵌套 车型

    MODEL_NAME = df['车型名称'].tolist()
    SPEC_ID = df['SPEC_ID'].tolist()
    YEAR_NAME = df['年代款'].tolist()
    YEAR_ID = df['年代款'].tolist()  # 设置year_id=year_name

    dic_model = dict(zip(SPEC_ID, MODEL_NAME))
    dic_year = dict(zip(YEAR_NAME, YEAR_ID))
    dic_key_id = dict(zip(SPEC_ID, YEAR_ID))
    for year_id in dic_year.keys():
        year_dic = {
            "yearId": "",
            "yearName": "",
            "modelList": []
        }
        year_dic["yearId"] = year_id
        year_dic["yearName"] = dic_year[year_id]
        for spec_id in SPEC_ID:
            if year_id == dic_key_id[spec_id]:
                model_dic = {
                    "modelId": "",
                    "modelName": ""
                }
                model_dic["modelId"] = spec_id
                model_dic["modelName"] = dic_model[spec_id]
                year_dic["modelList"].append(model_dic)
        re_list.append(year_dic)
    return re_list

# Config_get_model(104224)

# 读取配置数据
def Config_get_config_local(id_):
    id_ = int(id_)
    sql = """
            SELECT 
                 [BDCI_CHEXUN].[stg].[CONFIGURATION_DETAILS].[PARA_NAME]
                ,[PARA_VALUE]
            FROM 
                [BDCI_CHEXUN].[stg].[CONFIGURATION_DETAILS]
            JOIN 
                [BDCI_CHEXUN].[stg].[CONFIG_ITEM]
            ON
                [BDCI_CHEXUN].[stg].[CONFIGURATION_DETAILS].[PARA_NAME]=[BDCI_CHEXUN].[stg].[CONFIG_ITEM].[PARA_NAME]
            WHERE 
                [SPEC_ID]="""+str(id_)+"""
            ORDER BY 
                convert (int,PARA_ID)
            """
    conn = pymssql.connect(server, user, password, "BDCI")
    df = pd.read_sql_query(sql, conn)
    name = df['PARA_NAME'].tolist()
    value = df['PARA_VALUE'].tolist()
    dic_template = {	"基础参数":[
		"车型名称","年代款","厂商指导价","全国经销商最低价","实测100-0制动（m）","官方0-100加速（s）","实测油耗（L）","最高车速（km/h）","工信部综合油耗（L）",
		"排量(L)","长*宽*高(mm)","整车质保","车身结构","挡位个数","变速箱类型"],"车身参数":[
		"轴距(mm)","前轮距(mm)","后轮距(mm)","最小离地间隙(mm)","整备质量(Kg)","车门数(个)","座位数(个)","油箱容积(L)","行李箱容积(L)","前排宽度(mm)",
		"前排高度(mm)","前排腿部空间最小值(mm)","前排腿部空间最大值(mm)","前排坐垫长度(mm)","后排宽度(mm)","后排高度(mm)","后排腿部空间最小值(mm)","后排腿部空间最大值(mm)",
		"后排坐垫长度(mm)","后排中央地台高度(mm)","后备箱开启后宽度(mm)","后备箱开启后高度(mm)","后备箱开启后纵向深度(mm)","后备箱开启后放倒后排纵向深度(mm)"],"发动机参数":["发动机型号","汽缸容积(cc)","工作方式","汽缸排列形式","汽缸数(个)","每缸气门数(个)","压缩比","气门结构","缸径","冲程","最大马力(Ps)",
		"最大功率(kW)","最大功率转速(rpm)","最大扭矩(N·m)","最大扭矩转速(rpm)","发动机特有技术","燃料形式","燃油标号","供油方式","缸盖材料","缸体材料","环保标准"],"底盘转向参数":[
		"驱动方式","前悬挂类型","后悬挂类型","车体结构","助力类型","四驱形式","中央差速器结构"],"车轮制动参数":[
		"前制动器类型","后制动器类型","驻车制动类型","前轮胎规格","后轮胎规格","备胎规格"],"安全装备": [
		"主/副驾驶座安全气囊","前/后排侧气囊","前/后排头部气囊(气帘)","膝部气囊","胎压监测装置","安全带未系提示","零胎压继续行驶","车内中控锁",
		"发动机电子防盗","遥控钥匙","无钥匙启动系统","儿童安全座椅合"],"控制配置":[
		"制动防抱死系统(ABS)","制动力分配系统(EBD/CBC等)","制动辅助系统(EBA/BAS/BA等)","牵引力控制系统(ASR/TCS/TRC等)","车辆稳定控制系统(ESP/DSC/VSC等)",
		"自动驻车/上坡辅助系统","陡坡缓降系统","可调悬挂","空气悬挂","主动转向系统","前桥限滑差速器/差速锁","中央差速器锁止功能","后桥限滑差速器/差速锁"],"外部配置":[
		"电动/手动天窗","全景/电动全景天窗","运动外观套件","铝合金轮毂","电动吸合门"],"内部配置":[
		"真皮方向盘","方向盘调节","方向盘电动调节","多功能方向盘","方向盘换挡","定速巡航","倒车辅助/倒车雷达","可视倒车辅助","行车电脑显示屏","风挡投射显示系统(HUD)"],
                            "座椅配置":[
		"真皮/仿皮座椅","运动座椅","座椅高低调节","腰部支撑调节","肩部支撑调节","前排座椅电动调节","第二排靠背角度调节","第二排座椅前后调节","后排座椅电动调节",
		"座椅记忆","前/后排座椅加热","座椅通风","座椅按摩","后排座椅放倒方式","第三排座椅","前/后座中央扶手","后排杯架","电动后备箱门"],"多媒体配置":[
		"车载GPS导航系统","定位互动服务系统","中控台彩色显示屏","车辆交互系统(iDrive/MMI等)","内置硬盘存储空间","蓝牙/车载电话","车载电视","后排液晶屏","外接音源接口(AUX/USB/iPod等)",
		"CD支持MP3/WMA","多媒体系统","2-3只扬声器","4-5只扬声器","6-7只扬声器","≥8只扬声器"],"灯光配置":[
		"氙气大灯","日间行车灯","自动大灯","前雾灯","随动转向大灯/转向辅助灯","大灯高度自动/手动可调","大灯清洗装置","车内氛围灯","LED大灯"],"玻璃/后视镜":[
		"前/后电动车窗","车窗防夹手功能","防紫外线/隔热玻璃","外后视镜电动调节","外后视镜电加热","外后视镜电动折叠","外后视镜记忆功能","后视镜自动防眩目","后风挡遮阳帘",
		"后排侧遮阳帘","遮阳板化妆镜","后风挡雨刷","自动雨刷"],"空调/冰箱":[
		"空调控制方式","后排独立空调","后座出风口","温度分区控制","空气净化/花粉过滤","车载冰箱"],"高科技配置":[
		"自适应巡航系统","车辆行驶并线辅助系统","主动刹车/安全系统","整体主动转向系统","自动泊车辅助系统","可视夜视系统","中控液晶屏分屏显示","车辆全景影像系统"],"纯电动发动机参数":[
		"电池支持最高续航里程(km)","电池容量(kw/h)","电动机最大功率(kW)","电动机最大扭矩(N*m)"]
    }
    list_order = [	"基础参数",
		"车型名称","年代款","厂商指导价","全国经销商最低价","实测100-0制动（m）","官方0-100加速（s）","实测油耗（L）","最高车速（km/h）","工信部综合油耗（L）",
		"排量(L)","长*宽*高(mm)","整车质保","车身结构","挡位个数","变速箱类型",

	"车身参数",
		"轴距(mm)","前轮距(mm)","后轮距(mm)","最小离地间隙(mm)","整备质量(Kg)","车门数(个)","座位数(个)","油箱容积(L)","行李箱容积(L)","前排宽度(mm)",
		"前排高度(mm)","前排腿部空间最小值(mm)","前排腿部空间最大值(mm)","前排坐垫长度(mm)","后排宽度(mm)","后排高度(mm)","后排腿部空间最小值(mm)","后排腿部空间最大值(mm)",
		"后排坐垫长度(mm)","后排中央地台高度(mm)","后备箱开启后宽度(mm)","后备箱开启后高度(mm)","后备箱开启后纵向深度(mm)","后备箱开启后放倒后排纵向深度(mm)",

	"发动机参数",
		"发动机型号","汽缸容积(cc)","工作方式","汽缸排列形式","汽缸数(个)","每缸气门数(个)","压缩比","气门结构","缸径","冲程","最大马力(Ps)",
		"最大功率(kW)","最大功率转速(rpm)","最大扭矩(N·m)","最大扭矩转速(rpm)","发动机特有技术","燃料形式","燃油标号","供油方式","缸盖材料","缸体材料","环保标准",

	"底盘转向参数",
		"驱动方式","前悬挂类型","后悬挂类型","车体结构","助力类型","四驱形式","中央差速器结构",

	"车轮制动参数",
		"前制动器类型","后制动器类型","驻车制动类型","前轮胎规格","后轮胎规格","备胎规格",

	"安全装备",
		"主/副驾驶座安全气囊","前/后排侧气囊","前/后排头部气囊(气帘)","膝部气囊","胎压监测装置","安全带未系提示","零胎压继续行驶","车内中控锁",
		"发动机电子防盗","遥控钥匙","无钥匙启动系统","儿童安全座椅合",

	"控制配置",
		"制动防抱死系统(ABS)","制动力分配系统(EBD/CBC等)","制动辅助系统(EBA/BAS/BA等)","牵引力控制系统(ASR/TCS/TRC等)","车辆稳定控制系统(ESP/DSC/VSC等)",
		"自动驻车/上坡辅助系统","陡坡缓降系统","可调悬挂","空气悬挂","主动转向系统","前桥限滑差速器/差速锁","中央差速器锁止功能","后桥限滑差速器/差速锁",

	"外部配置",
		"电动/手动天窗","全景/电动全景天窗","运动外观套件","铝合金轮毂","电动吸合门",

	"内部配置",
		"真皮方向盘","方向盘调节","方向盘电动调节","多功能方向盘","方向盘换挡","定速巡航","倒车辅助/倒车雷达","可视倒车辅助","行车电脑显示屏","风挡投射显示系统(HUD)",

	"座椅配置",
		"真皮/仿皮座椅","运动座椅","座椅高低调节","腰部支撑调节","肩部支撑调节","前排座椅电动调节","第二排靠背角度调节","第二排座椅前后调节","后排座椅电动调节",
		"座椅记忆","前/后排座椅加热","座椅通风","座椅按摩","后排座椅放倒方式","第三排座椅","前/后座中央扶手","后排杯架","电动后备箱门",

	"多媒体配置",
		"车载GPS导航系统","定位互动服务系统","中控台彩色显示屏","车辆交互系统(iDrive/MMI等)","内置硬盘存储空间","蓝牙/车载电话","车载电视","后排液晶屏","外接音源接口(AUX/USB/iPod等)",
		"CD支持MP3/WMA","多媒体系统","2-3只扬声器","4-5只扬声器","6-7只扬声器","≥8只扬声器",

	"灯光配置",
		"氙气大灯","日间行车灯","自动大灯","前雾灯","随动转向大灯/转向辅助灯","大灯高度自动/手动可调","大灯清洗装置","车内氛围灯","LED大灯",

	"玻璃/后视镜",
		"前/后电动车窗","车窗防夹手功能","防紫外线/隔热玻璃","外后视镜电动调节","外后视镜电加热","外后视镜电动折叠","外后视镜记忆功能","后视镜自动防眩目","后风挡遮阳帘",
		"后排侧遮阳帘","遮阳板化妆镜","后风挡雨刷","自动雨刷",

	"空调/冰箱",
		"空调控制方式","后排独立空调","后座出风口","温度分区控制","空气净化/花粉过滤","车载冰箱",

	"高科技配置",
		"自适应巡航系统","车辆行驶并线辅助系统","主动刹车/安全系统","整体主动转向系统","自动泊车辅助系统","可视夜视系统","中控液晶屏分屏显示","车辆全景影像系统",

	"纯电动发动机参数",
		"电池支持最高续航里程(km)","电池容量(kw/h)","电动机最大功率(kW)","电动机最大扭矩(N*m)"
]
    dic_use = dict(zip(name, value))
    list_value = []
    re_list_m = []
    list_name = []
    k = []

    for name_ in list_order:
        for name__ in dic_use.keys():
            if name_ == name__:
                list_value.append(dic_use[name_])

    for key in dic_template.keys():
        list_name = list_name+dic_template[key]

    for i in list_order:
        if i in list_name:
            re_list_m.append('')
        else:
            re_list_m.append(i)

    # 删除多余行
    for i in range(len(re_list_m)-16):
        if re_list_m[i] is not "":
            del re_list_m[i+1]

    # 空值替换为name的类
    for i in range(len(re_list_m)):
        if re_list_m[i] != '':
            target = re_list_m[i]
        else:
            re_list_m[i] = target

    for key in dic_template.keys():
        k.append(key)

    re_dic_ = {"name": list_name, "value": list_value, "m": re_list_m, "k": k}
    return re_dic_

# Config_get_config_local(108517)
