# -*- coding: utf-8 -*-

import ast
import time
from configparser import ConfigParser

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
        ('日期', '航班', '始发城市', '目的城市', '航线', '时间', '耗时', '畅飞卡座位'),
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
    headers = config['header']['headers']
    url = config['url']['AvFare']
    headers = ast.literal_eval(headers)  # 字符串转字典，使用literal_eval更安全，避免了 json 包的双引号问题
    response = requests.post(url=url, headers=headers,
                             data=data).json()

    errorInfo = response.get("errorInfo")
    flightInfoList = response.get("flightInfoList")

    if flightInfoList == None or flightInfoList == []:
        pass
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
                    if cabinNumber == 'A':
                        cabinNumber = '可兑换'
                    else:
                        cabinNumber = cabinNumber
                    content = (flightDate, carrierNoName, depCityName, arrCityName,
                               depCityName + depAirportName + depTerm + '->' + arrCityName + arrAirportName + arrTerm,
                               depDateTime + '~' + arrDateTime, duration, cabinNumber)
                    return content


if __name__ == '__main__':
    allFlights = get_place()
    blackBox = config['blackBox']['blackBox']
    dataList = []
    contentList = []
    departureDate = "2020-10-20"
    for i in range(len(allFlights)):
        departureCity = allFlights[i].get('departureCity')
        if departureCity == '长沙':
            sendCode = allFlights[i].get('长沙')
            allowFlights = allFlights[i].get('allowFlights')
            for arrCode in allowFlights.keys():
                data = '{"directType": "D", "flightType": "OW","tripType": "D","arrCode": "%s","sendCode": "%s",' \
                       '"departureDate": "%s","blackBox": "%s"}' % (arrCode, sendCode, departureDate, blackBox)
                # dataList.append(data)
                content = get_flight_ticket(data)
                if content != None:
                    contentList.append(str(content))
            rowData = ','.join(contentList)
            html = output_html(rowData)
            print(html)
    # pool = multiprocessing.Pool(processes=10)  # 100 个进程
    # # 多进程
    # pool.map(get_flight_ticket, dataList)  # 列表，迭代器
    # pool.close()
    # pool.join()
