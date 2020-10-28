# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import ast
import datetime
import glob
import os
import random
import time
from configparser import ConfigParser

import pandas as pd
import requests

from PlaceSpider import get_place

config = ConfigParser()
config.read('Info.ini', encoding='UTF-8')


def save_header(departureDate):
    csvPath = os.getcwd() + '/' + str(departureDate) + '.csv'
    header = [('更新时间', '日期', '始发城市', '目的城市', '航班', '航线', '时间', '耗时', '畅飞卡座位')]
    header = pd.DataFrame(header)
    header.to_csv(csvPath, index=False, header=False, mode='a')


# 将每天的航班信息保存为 CSV 文件
def save_csv(departureDate, rowData):
    csvPath = os.getcwd() + '/' + str(departureDate) + '.csv'
    dataFrame = pd.DataFrame([rowData])
    dataFrame.to_csv(csvPath, index=False, header=False, mode='a')
    print(departureDate, rowData, '数据导入成功')


# 将每天的航班 CSV 文件保存到 excel
def save_excel(today):
    with pd.ExcelWriter('{}.xlsx'.format(today)) as writer:
        csvRoot = '.'
        csvPath = '*.csv'
        for csvFile in glob.glob(os.path.join(csvRoot, csvPath)):
            data = pd.read_csv(csvFile)
            data.to_excel(writer, sheet_name=csvFile[7:][:5])
            print(csvFile[7:][:5], 'csv迁移至 excel 成功')
    writer.save()
    writer.close()


# 删除所有 CSV 文件
def delete_all_csv():
    csvRoot = '.'
    csvPath = '*.csv'
    for csvFile in glob.glob(os.path.join(csvRoot, csvPath)):
        os.remove(csvFile)
    print('清除所有 CSV 文件成功')


# 得到航班余票信息
def get_flight_ticket(departureDate, data):
    carrierList = []
    requestTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 请求航班数据接口时间
    headers = config['header']['headers']
    url = config['url']['AvFare']
    # 字符串转字典，使用literal_eval更安全，避免了 json 包的双引号问题
    headers = ast.literal_eval(headers)
    response = requests.post(url=url, headers=headers,
                             data=data).json()
    # time.sleep(random.randint(1, 4))
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
        if carrierList is not None:
            for row in range(len(carrierList)):
                # eval 去掉字符串的双引号
                tupleData = tuple(eval(carrierList[row]))
                save_csv(departureDate, tupleData)


if __name__ == '__main__':
    allFlights = get_place()
    # blackBox = config['blackBox']['blackBox']
    blackBoxList = [
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjEyNTcsInQiOiJ0WFVmdi9FRHJFaWxralV3RGg3TlYzQVdxb2xaNDJmVFJ2SnZzL05Melp1aS9yT3FXd05pQ0E3ZmtwZ3lySXQxcXR1cE9jNUxnZ2g0RFFCRW9JSkhMZz09In0=',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjEwNzMsInQiOiJJZDQwZ2FzRWdFb3Jic1ZsUnlaZnpad0xKbm84OXpVMmd2SlUrS05HQlRyQnlqNHF1NThoRlpUMkdlUEtDeUdTUlBTTk1xaTRPS3dtajRwTHU4UlZBdz09In0=',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjI4NDksInQiOiJrTVNmWTdOd0gvOWFuak9KcktXM2NHWk9md0ZkVkFsdHRzSytoTzZWZUMwK1pBQ1RWbVdGNDZlb3c2NGZrbk1oc3ZPdys0WVViRjRLbUdrOStnT2UvQT09In0=',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjMxOSwidCI6InlVRWN3cHFTVi9PNmU5UkpsQmxoclRoZm1wMlplb25ZL3JZM2xZSVlVMithL0hwbkZpempXT0ZxQTJWLzFaTk56eXVzUjR6QjFNYlh0a3czZUFFQUh3PT0ifQ==',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjgzOCwidCI6IkFrREd5WUdvN3JWNm9ROVhYK1o0cWtxeXN4U29zU1E5bVRZRTVLMmhLNklIZTdsdVJ6RlN1Rkh4S1lzVks1ZmtTMGM1ZEZUbDRUNXZkbU41eUJQa0R3PT0ifQ==',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjEwNDAsInQiOiJYRjVDcitzUzIzYTFFaXJVZkxOaTgydWFSaitaWUFoV0Z4Tk90WUtCUW1uWVZuUDU0cTRaMUFnU3lwR3NDbXllNnJtWjA1UnU1NkswS1BHdlRjZjVWQT09In0==',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjk4MCwidCI6IkdEVEpLU3QwdmFxd21KQk1XRUwvQnU5TzlVQkRKODE0eXJyc3pRbmEzYndEQTJ4SjJlTC9XN1VKZVlIVUNMTDE0QlBya3M4ZnhmRE1OWUZlR2V4dGtRPT0ifQ',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjE5MjEsInQiOiJWbG1qcDJOcjE2bk1lSFMzL3ZLR1o5M2NhenZvNjRQczBaZ1pINlRJN3dnbFFUanFSbWRhOG5JZXJwTVRTU3ZOYjZMTU02U3d5T1VzMytnU1hIWVRpdz09In0=']
    dataList = []  # 目的地列表
    contentList = []  # 每天的航班信息列表，只用于输出 html
    createTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    processStartTime = datetime.datetime.now()
    today = datetime.date.today()
    for day in range(5, 35):
        # time.sleep(random.randint(1, 10))
        departureDate = today + datetime.timedelta(days=day)
        weekDay = departureDate.weekday()
        # 选择近 30 天的周五周六
        if weekDay == 4 or weekDay == 5:
            save_header(departureDate)
            for i in range(len(allFlights)):
                departureCity = allFlights[i].get('departureCity')
                if departureCity == '上海':
                    sendCode = allFlights[i].get('上海')
                    allowFlights = allFlights[i].get('allowFlights')
                    for arrCode in allowFlights.keys():
                        data = '{"directType": "D", "flightType": "OW","tripType": "D","arrCode": "%s","sendCode": "%s",' \
                               '"departureDate": "%s","blackBox": "%s"}' % (
                               arrCode, sendCode, departureDate, random.choice(blackBoxList))
                        # dataList.append(data)  # 多进程用这个，注释取消

                        oneCarrier = get_flight_ticket(departureDate, data)  # 单进程用这个

    # pool = multiprocessing.Pool(processes=4)  # 进程
    #
    # # 多进程
    # pool.map(get_flight_ticket, dataList)  # 列表，迭代器
    # pool.close()
    # pool.join()

    save_excel(today)  # 保存 csv 到 excel
    delete_all_csv()  # 删除所有 csv
    processEndTime = datetime.datetime.now()
    processConsumingTime = (processEndTime - processStartTime).seconds
    print(createTime, '该次任务总共耗时：{} 分钟'.format(processConsumingTime / 60))
