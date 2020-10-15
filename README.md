# OriginRemainTickets


# PlaceSpider.py
## 用途
1. 获取所有出发地对应的航线（如上海 -> （长沙 / 南京 / 北京 / 。。。。））
2. 通过 import 方式，给 AllowFlightSpider.py 使用

# AllowFlightSpider.py

## 用途
1. 爬取「x始发地」 吉祥航空近 30 天的畅飞卡余票信息并保存到数据库
2. （待选）将余票信息以 html 内容输出

## 数据库格式

| 序号 | 字段 | 类型 | 注释 |
|-|-|-|-|
| 1 | create_time | timestamp | 创建时间，一次爬虫任务生成的信息时间相同 |
| 2 | flight_date | date | 航班日期，一次爬虫任务的日期有 5~35 天后 |
| 3 | dep_city_name | varchar | 出发城市 |
| 4 | arr_city_name | varchar | 到达城市 |
| 5 | carrier_no_name | varchar | 航班号 |
| 6 | fly_time | varchar | 飞行时间 |
| 7 | air_route | varchar | 飞行日期 |
| 8 | duration | varchar | 飞行耗时 |
| 9 | cabinbumber | varchar | 吉祥航空畅飞卡余票信息 |


