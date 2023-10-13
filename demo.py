import time

import requests
import json
from datetime import datetime
import random
#01 walking
def direction_walking(origin,destination,output,key):
    url=f'https://restapi.amap.com/v3/direction/walking?origin={origin}&destination={destination}&output={output}&key={key}'
    #print(url)
    response = requests.get(url)
    data = response.json()
    #print(data)
    # 处理 JSON 数据
    status=data['status'] #值为0或1 1：成功；0：失败
    info=data['info'] #	status为0时，info返回错误原；否则返回“OK”。详情参阅info状态表
    if status=='0':
        print('错误原因 '+info)
        return {"origin":origin,"destination":destination,"way":"walking","info":info}
    count=data['count'] #结果总数目
    route=data['route'] #路线信息列表
    origin=route['origin']
    destination=route['destination']
    paths=route['paths']
    polylines=[]
    mypaths=[]
    for path in paths:
        distance=path['distance']
        duration=path['duration']
        steps=path['steps']
        polyline=[] #存储此步行方案所有的坐标点
        for step in steps:
            step_polyline=step['polyline']	#此路段坐标点
            polyline.extend(step_polyline.split(';'))
        polylines.append(polyline)
        steps=";".join(polyline)
        path={
            "distance":distance,
            "duration":duration,
            "polyline":steps
        }
        mypaths.append(path)
    return {"origin":origin,"destination":destination,"way":"walking",
             "info":info,"paths":mypaths}
#02 transit
def direction_transit(origin,destination,output,city,key):
    url=f'https://restapi.amap.com/v3/direction/transit/integrated?key={key}&origin={origin}&destination={destination}&output={output}&city={city}&cityd={city}&strategy=0&nightflag=0'
    #print(url)
    response = requests.get(url)
    data = response.json()
    #print(data)
    # 处理 JSON 数据
    status=data['status'] #值为0或1 1：成功；0：失败
    info=data['info'] #	status为0时，info返回错误原；否则返回“OK”。详情参阅info状态表
    if status=='0':
        print('错误原因 '+info)
        return {"origin": origin, "destination": destination, "way": "transit", "info": info}

    count=int(data['count']) #公交换乘方案数目
    route=data['route'] #公交换乘信息列表
    origin=route['origin']
    destination=route['destination']
    od_walking_distance=route['distance']  #起点和终点的步行距离
    taxi_cost=route['taxi_cost']
    transits=route['transits']
    #遍历显示各种公交换乘方案
    for transit in transits:
        cost=transit['cost']
        duration=transit['duration']
        nightflag=transit['nightflag']
        walking_distance=transit['walking_distance']
        distance=transit['distance']
        missed=transit['missed']
        segments=transit['segments']
        for segment in segments:
            taxi=segment['taxi']
            walking=segment['walking']#此路段步行导航信息
            bus=segment['bus']#此路段公交导航信息
            entrance=segment['entrance']#地铁入口
            exit=segment['exit']#地铁出口
            railway=segment['railway']#乘坐火车的信息
    return {"origin":origin,"destination":destination,"way":"transit",
             "info":info,"route":route}
#03 driving
def direction_driving(origin,destination,output,key,strategy):
    url=f'https://restapi.amap.com/v3/direction/driving?origin={origin}&destination={destination}&output={output}&key={key}&strategy={strategy}&waypoints=&extensions=base'
    #print(url)
    response = requests.get(url)
    data = response.json()
    #print(data)
    # 处理 JSON 数据
    status=data['status'] #值为0或1 1：成功；0：失败
    info=data['info'] #	status为0时，info返回错误原；否则返回“OK”。详情参阅info状态表
    if status=='0':
        print('错误原因 '+info)
        return {"origin":origin,"destination":destination,"way":"driving","info":info}
    count=data['count'] #结果总数目
    route=data['route'] #路线信息列表
    origin=route['origin']
    destination=route['destination']
    paths=route['paths']
    mypaths=[]
    for path in paths:
        distance=path['distance']
        duration=path['duration']
        strategy=path['strategy']
        tolls=path['tolls']#此导航方案道路收费
        toll_distance=path['toll_distance']#收费路段距离
        restriction=path['restriction']#限行结果 0 代表限行已规避或未限行，即该路线没有限行路段1 代表限行无法规避，即该线路有限行路段
        traffic_lights=path['traffic_lights']
        steps=path['steps']
        polyline=[] #存储此步行方案所有的坐标点
        for step in steps:
            step_polyline=step['polyline']	#此路段坐标点
            polyline.extend(step_polyline.split(';'))
        steps = ";".join(polyline)
        path = {
            "distance": distance,
            "duration": duration,
            "polyline": steps
        }
        mypaths.append(path)
    return {"origin":origin,"destination":destination,"way":"driving",
             "info":info,"paths":mypaths}
#04 bicycling
def direction_bicycling(origin,destination,output,key):
    url=f'https://restapi.amap.com/v4/direction/bicycling?origin={origin}&destination={destination}&key={key}'
    #print(url)
    response = requests.get(url)
    data = response.json()
    #print(data)
    # 处理 JSON 数据
    errcode=data['errcode'] #0，表示成功
    errdetail=data['errdetail']
    errmsg=data['errmsg']
    if errcode!=0:
        print('错误原因 '+errdetail)
        return {"origin": origin, "destination": destination, "way": "bicycling","info": errmsg}
    destination=data['data']['destination']
    origin=data['data']['origin']
    paths=data['data']['paths']
    mypaths=[]
    for path in paths:
        distance=path['distance']
        duration=path['duration']
        steps=path['steps']
        polyline=[] #存储此步行方案所有的坐标点
        instruction=[]
        for step in steps:
            step_polyline=step['polyline']	#此路段坐标点
            step_instruction=step['instruction']	#此路段骑行指示
            polyline.extend(step_polyline.split(';'))
            instruction.append(step_instruction)
        steps = ";".join(polyline)
        path = {
            "distance": distance,
            "duration": duration,
            "polyline": steps
        }
        mypaths.append(path)
    return {"origin":origin,"destination":destination,"way":"bicycling",
             "info":errmsg,"paths":mypaths}
def generate_point():
    # 广州市番禺区的经度范围
    longitude_range = (113.2, 113.4)
    # 广州市番禺区的纬度范围
    latitude_range = (22.9, 23.1)
    # 生成随机经度
    longitude = round(random.uniform(*longitude_range), 6)
    # 生成随机纬度
    latitude = round(random.uniform(*latitude_range), 6)
    # 返回经纬度坐标
    return f'{longitude},{latitude}'
def generate_data():
    #origin = '113.405427,23.048538'  # 华工大学城校区
    #destination = '116.587922,40.081577'  # 华工五山校区
    #destination = '113.390579,23.065123'  # 中山大学东校区
    for i in range(100000):
        # 获取当前时间
        now = datetime.now()
        # 提取时、分、秒
        hour = now.hour
        minute = now.minute
        second = now.second
        current = f'{hour}:{minute}:{second}'
        origin=generate_point()
        destination=generate_point()
        output = 'json'
        key = 'b04b0ec7d62dfcc0a4f87f35600f009d'
        walking_data = direction_walking(origin, destination, output, key)
        transit_data = direction_transit(origin, destination, output, "广州", key)
        driving_data = direction_driving(origin, destination, output, key, 0)
        bicycling_data = direction_bicycling(origin, destination, output, key)
        data = {
            "time": current,
            "origin": origin,
            "destination": destination,
            "walking_data": walking_data,
            "transit_data": transit_data,
            "driving_data": driving_data,
            "bicycling_data": bicycling_data
        }
        print(data)
        with open("data.json", "a") as file:
            json.dump(data, file)
        time.sleep(30)
if __name__=='__main__':
    generate_data()
