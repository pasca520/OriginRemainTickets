# -*- coding: utf-8 -*-

import ast
import datetime
import time
import random
from configparser import ConfigParser

import pymysql
import requests
from HTMLTable import HTMLTable

from PlaceSpider import get_place

config = ConfigParser()
config.read('Info.ini', encoding='UTF-8')


# 输出 html 内容
def output_html(rowData):
    """
    :param rowData: 行数据, 元祖数据，逗号分隔，格式为(
        ('2020/10/18', 'HO1234', '上海', '上海', '10:00~12:00', '可兑换'),
        ('2020/10/18', 'HO1234', '上海', '上海', '10:00~12:00', '可兑换'),)
    :return: html 内容
    """
    nowTime = time.strftime('%Y-%m-%d %H:%M:%S')
    # 标题
    table = HTMLTable(caption='吉祥航空畅心飞余票概览(%s更新)' % nowTime)
    table.append_header_rows((
        ('日期', '始发城市', '目的城市', '航班', '航线', '时间', '耗时', '畅飞卡座位'),
    ))

    # 表格内容
    table.append_data_rows(rowData)

    # 表格样式，即<table>标签样式
    table.set_style({
        'border-collapse': 'collapse',

        'word-break': 'keep-all',
        'white-space': 'nowrap',
        'font-size': '14px',
    })

    # 统一设置所有单元格样式，<td>或<th>
    table.set_cell_style({
        'border-color': '#000',
        'border-width': '1px',
        'border-style': 'solid',
        'padding': '5px',
    })

    # 表头样式
    table.set_header_row_style({
        'color': '#fff',
        'background-color': '#48a6fb',
        'font-size': '18px',
    })

    # 覆盖表头单元格字体样式
    table.set_header_cell_style({
        'padding': '15px',
    })
    html = table.to_html()
    return html


# 得到航班余票信息
def get_flight_ticket(data):
    carrierList = []
    requestTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 请求航班数据接口时间
    headers = config['header']['headers']
    url = config['url']['AvFare']
    # 字符串转字典，使用literal_eval更安全，避免了 json 包的双引号问题
    headers = ast.literal_eval(headers)
    response = requests.post(url=url, headers=headers,
                             data=data).json()
    time.sleep(random.randint(1, 4))
    errorInfo = response.get("errorInfo")
    flightInfoList = response.get("flightInfoList")
    if flightInfoList is None or flightInfoList == []:
        print(requestTime, '获取航班数据异常', '报错:%s' % errorInfo)
    elif errorInfo == '成功':
        for flightInfo in flightInfoList:
            for cabinFare in flightInfo['cabinFareList']:
                if cabinFare['cabinCode'] == 'X':
                    carrierNoName = flightInfo.get('carrierNoName')  # 航班，如吉祥HO1054
                    arrCityName = flightInfo.get('arrCityName')  # 到达城市，如虹桥
                    arrAirportName = flightInfo.get('arrAirportName')  # 到达机场，如虹桥
                    arrTerm = flightInfo.get('arrTerm')  # 到达航站楼
                    arrDateTime = flightInfo.get('arrDateTime')[-5:]  # 到达时间
                    flightDate = flightInfo.get('flightDate')  # 航班日期
                    depCityName = flightInfo.get('depCityName')  # 出发城市
                    depAirportName = flightInfo.get('depAirportName')  # 出发机场
                    depTerm = flightInfo.get('depTerm')  # 出发航站楼
                    depDateTime = flightInfo.get('depDateTime')[-5:]  # 出发时间
                    duration = flightInfo.get('duration')  # 航班耗时
                    duration = time.strftime("%H时%M分", time.gmtime(duration / 1000))  # 耗时转换为小时分钟
                    cabinNumber = cabinFare['cabinNumber']  # 余票
                    airRoute = depCityName + depAirportName + depTerm + '->' + arrCityName + arrAirportName + arrTerm  # 航线
                    flyTime = depDateTime + '~' + arrDateTime  # 时间
                    if cabinNumber == 'A':
                        cabinNumber = '可兑换'
                    else:
                        cabinNumber = cabinNumber
                    content = "'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}'".format(createTime, flightDate,
                                                                                            depCityName,
                                                                                            arrCityName, carrierNoName,
                                                                                            airRoute, flyTime,
                                                                                            duration, cabinNumber)
                    if content is not None:
                        carrierList.append(str(content))
        # return carrierList
        # print(carrierList)
        if carrierList != None:
            for row in range(len(carrierList)):
                save_to_db(str(carrierList[row]))


def save_to_db(rowData):
    passWord = config['database']['passWord']
    databaseName = config['database']['databaseName']
    wirteTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 写入数据库时间
    db = pymysql.connect("localhost", "root", passWord, databaseName)  # 打开数据库连接
    cursor = db.cursor()  # 使用 cursor() 方法创建一个游标对象 cursor
    sql = """INSERT INTO unlimited_fly_tickets (create_time, flight_date, dep_city_name, arr_city_name, carrier_no_name, air_route, fly_time, duration, cabinbumber) VALUES ({})""".format(
        rowData)  # SQL 插入语句
    try:
        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 提交到数据库执行
        print(wirteTime, "成功写入表中", rowData)
    except BaseException:
        db.rollback()  # 如果发生错误则回滚
        db.show_warnings()
        print(wirteTime, "写入表失败", rowData)
    db.close()  # 关闭数据库连接


if __name__ == '__main__':
    allFlights = get_place()
    blackBox = config['blackBox']['blackBox']
    dataList = []  # 目的地列表
    contentList = []  # 每天的航班信息列表，只用于输出 html
    createTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    processStartTime = datetime.datetime.now()

    today = datetime.date.today()
    for day in range(5, 35):
        time.sleep(random.randint(1, 10))
        departureDate = today + datetime.timedelta(days=day)
        for i in range(len(allFlights)):
            departureCity = allFlights[i].get('departureCity')
            if departureCity == '上海':
                sendCode = allFlights[i].get('上海')
                allowFlights = allFlights[i].get('allowFlights')
                for arrCode in allowFlights.keys():
                    data = '{"directType": "D", "flightType": "OW","tripType": "D","arrCode": "%s","sendCode": "%s",' \
                           '"departureDate": "%s","blackBox": "%s"}' % (arrCode, sendCode, departureDate, blackBox)
                    # dataList.append(data)
                    get_flight_ticket(data)
                # if content != None :
                #     for row in range(len(content)):
                #         save_to_db(contentList[row])
        # for j in range(len(contentList)):
        #     save_to_db(contentList(j))

    # 输出到 html 模块，不用可注释
    # rowData = ','.join(contentList)
    # rowData = '({})'.format(rowData)
    # html = output_html(rowData)
    # print(html)
    # print(rowData)

    # pool = multiprocessing.Pool(processes=20)  # 100 个进程
    #
    # # 多进程
    # pool.map(get_flight_ticket, dataList)  # 列表，迭代器
    # pool.close()
    # pool.join()

    processEndTime = datetime.datetime.now()
    processConsumingTime = (processEndTime - processStartTime).seconds
    print(createTime, '该次任务总共耗时：{} 分钟'.format(processConsumingTime/60))
