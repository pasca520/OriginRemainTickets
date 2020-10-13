# -*- coding: utf-8 -*-
from configparser import ConfigParser
import ast
import requests

config = ConfigParser()
config.read('Info.ini', encoding='UTF-8')
headers = config['header']['headers']
headers = ast.literal_eval(headers)  # 字符串转字典，使用literal_eval更安全，避免了 json 包的双引号问题
url = config['url']['flightLine']

def get_place():
    allFlightsList = []
    data = '{"channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}'
    response = requests.post(url=url, headers= headers, data=data).json()
    objData = response.get('objData')
    for i in range(len(objData)):
        allFlights = {}
        allowFlights = {}
        cityCode = objData[i].get('cityCode')
        cityName = objData[i].get('cityName')
        countryCode = objData[i].get('countryCode')
        airline = objData[i].get('airline')
        if countryCode == 'CN':
            allFlights['departureCity'] = cityName
            allFlights[cityName] = cityCode
            for j in range(len(airline)):
                allowCityCode = airline[j].get('cityCode')
                allowCityName = airline[j].get('cityName')
                allowCountryCode = airline[j].get('countryCode')
                if allowCountryCode == 'CN':
                    allowFlights[allowCityCode] = allowCityName
            allFlights['allowFlights'] = allowFlights
            allFlightsList.append(allFlights.copy())
    return allFlightsList


if __name__ == '__main__':
    allFlights = get_place()
