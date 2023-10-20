import time
import math
import requests
import json
from datetime import datetime
import random
# 封装发送请求的函数，含处理错误请求
def get_response_json(url):
    max_retries = 100
    if url.find("walking")!=-1 or url.find("transit")!=-1 or url.find("driving")!=-1:
        retries=1
        while retries<=max_retries:
            try:
                response_json = requests.get(url=url).json()
                status = response_json['status'] # 值为0或1 1：成功；0：失败
                if status=="1":
                    print(response_json)
                    return response_json
            except:
                print(f"请求出错， 尝试第 {retries}/{max_retries} 次重连中...")
                retries+=1
        exit(0)
    else:
        retries=1
        while retries<=max_retries:
            try:
                response_json = requests.get(url=url).json()
                errcode = response_json['errcode'] # 值为0或1 0：成功；1：失败
                if errcode==0:
                    print(response_json)
                    return response_json
            except:
                print(f"bicycling 请求出错， 尝试第 {retries}/{max_retries} 次重连中...")
                retries+=1
        exit(0)
#01 walking
def direction_walking(origin,destination,output,key):
    url=f'https://restapi.amap.com/v3/direction/walking?origin={origin}&destination={destination}&output={output}&key={key}'
    #print(url)
    data = get_response_json(url)
    #print(data)
    # 处理 JSON 数据
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
    return {"origin":origin,"destination":destination,"way":"walking","paths":mypaths}
#02 transit
def direction_transit(origin, destination, output, city, key):
    url = f'https://restapi.amap.com/v3/direction/transit/integrated?key={key}&origin={origin}&destination={destination}&output={output}&city={city}&cityd={city}&strategy=0&nightflag=0'
    # print(url)
    data = get_response_json(url)
    # print(data)
    # 处理 JSON 数据
    count = int(data['count'])  # 公交换乘方案数目
    route = data['route']  # 公交换乘信息列表
    origin = route['origin']
    destination = route['destination']
    od_walking_distance = route['distance']  # 起点和终点的步行距离
    taxi_cost = route['taxi_cost']
    transits = route['transits']  # 公交换乘方案列表
    my_transits = []  # 公交换乘方案列表
    # 遍历显示各种公交换乘方案
    for transit in transits:
        cost = transit['cost']
        duration = transit['duration']
        nightflag = transit['nightflag']
        walking_distance = transit['walking_distance']
        distance = transit['distance']
        missed = transit['missed']
        segments = transit['segments']
        transit_data=[]
        for segment in segments:
            taxi = segment['taxi']
            walking = segment['walking']  # 此路段步行导航信息
            segment_walking_data={}
            if len(walking)!=0:
                walking_origin = walking["origin"]
                walking_destination = walking["destination"]
                walking_distance = walking["distance"]
                walking_duration = walking["duration"]
                walking_steps = walking["steps"]
                walking_polyline = []  # 存储此步行方案所有的坐标点
                for step in walking_steps:
                    step_polyline = step['polyline']  # 此路段坐标点
                    walking_polyline.extend(step_polyline.split(';'))
                walking_polyline = ";".join(walking_polyline)
                segment_walking_data = {
                    "origin": walking_origin,
                    "destination": walking_destination,
                    "distance": walking_distance,
                    "duration": walking_duration,
                    "polyline": walking_polyline
                }
            bus = segment['bus']  # 此路段公交导航信息
            buslines = bus["buslines"]
            buslines_data = {}
            if len(buslines)!=0:
                for busline in buslines:
                    departure_stop = busline["departure_stop"]
                    arrival_stop = busline["arrival_stop"]
                    bus_polyline = busline["polyline"]
                    bus_type=busline["type"]
                    bus_duration=busline["duration"]
                    bus_distance=busline["distance"]
                    buslines_data={
                        "departure_stop": departure_stop,
                        "arrival_stop": arrival_stop,
                        "type": bus_type,
                        "duration":bus_duration,
                        "distance":bus_distance,
                        "bus_polyline": bus_polyline
                    }
            segment_bus_data = buslines_data

            entrance = segment['entrance']  # 地铁入口
            exit = segment['exit']  # 地铁出口
            railway = segment['railway']  # 乘坐火车的信息
            segment_railway_data = {}
            if "time" in railway.keys():
                railway_time = railway["time"]
                railway_distance = railway["distance"]
                railway_origin = railway["departure_stop"]
                railway_destination = railway["arrival_stop"]
                segment_railway_data = {
                    "time": railway_time,
                    "distance": railway_distance,
                    "origin": railway_origin,
                    "destination": railway_destination
                }
            transit_data.append({
                "walking":segment_walking_data,
                "bus":segment_bus_data,
                "railway":segment_railway_data
            })
        my_transits.append(transit_data)

    return {"origin": origin, "destination": destination, "way": "transit", "transits": my_transits}
#03 driving
def direction_driving(origin,destination,output,key,strategy):
    url=f'https://restapi.amap.com/v3/direction/driving?origin={origin}&destination={destination}&output={output}&key={key}&strategy={strategy}&waypoints=&extensions=base'
    #print(url)
    data = get_response_json(url)
    #print(data)
    # 处理 JSON 数据
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
    return {"origin":origin,"destination":destination,"way":"driving","paths":mypaths}
#04 bicycling
def direction_bicycling(origin,destination,output,key):
    url=f'https://restapi.amap.com/v4/direction/bicycling?origin={origin}&destination={destination}&key={key}'
    #print(url)
    data = get_response_json(url)
    #print(data)
    # 处理 JSON 数据
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
    return {"origin":origin,"destination":destination,"way":"bicycling","paths":mypaths}
def calculate_distance(lat1, lon1, lat2, lon2):
    # 将经纬度转换为弧度
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # 应用 Haversine 公式计算距离
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c  # 地球平均半径为6371公里
    return distance

def generate_random_point(center_lat, center_lon, max_distance):
    # 将中心点的经纬度转换为弧度
    center_lat_rad = math.radians(center_lat)
    center_lon_rad = math.radians(center_lon)

    # 将最大距离转换为弧度
    max_distance_rad = max_distance / 6371  # 6371是地球平均半径

    random_distance_rad = math.sqrt(random.uniform(0, 1)) * max_distance_rad
    random_bearing_rad = random.uniform(0, 2*math.pi)

    # 计算随机点的纬度和经度
    random_lat_rad = math.asin(math.sin(center_lat_rad) * math.cos(random_distance_rad) +
                               math.cos(center_lat_rad) * math.sin(random_distance_rad) * math.cos(random_bearing_rad))
    random_lon_rad = center_lon_rad + math.atan2(math.sin(random_bearing_rad) * math.sin(random_distance_rad) * math.cos(center_lat_rad),
                                                 math.cos(random_distance_rad) - math.sin(center_lat_rad) * math.sin(random_lat_rad))

    # 将随机点的纬度和经度转换为度数,小数点后保留6位
    random_lat = round(math.degrees(random_lat_rad), 6)
    random_lon = round(math.degrees(random_lon_rad), 6)

    return random_lat, random_lon
def generate_od_pair():
    # #以珠江新城为中心，半径5公里
    center_lat = 23.1192
    center_lon = 113.3212

    # 生成150个距离中心点5公里以内的随机点,作为起点
    origin_points = [] # 起点
    od_pair={}        # od对
    max_distance = 5  # 最大距离为5公里
    min_distance = 1  # 起点终点之间相距最小距离1公里
    while len(origin_points) < 150:
        random_lat, random_lon = generate_random_point(center_lat, center_lon, max_distance)
        distance = calculate_distance(center_lat, center_lon, random_lat, random_lon)
        if distance <= max_distance:
            origin_points.append((random_lat, random_lon))

    # 为每个起点生成150个终点
    for origin_point in origin_points:
        destination_points=[]
        while len(destination_points) < 150:
            random_lat, random_lon = generate_random_point(center_lat, center_lon, max_distance)
            center_distance = calculate_distance(center_lat, center_lon, random_lat, random_lon)
            od_distance=calculate_distance(origin_point[0], origin_point[1], random_lat, random_lon)
            if center_distance <= max_distance and od_distance>=min_distance:
                destination_points.append((random_lat, random_lon))
            od_pair[origin_point]=destination_points
    return od_pair
def generate_data():
    #origin = '113.405427,23.048538'  # 华工大学城校区
    #destination = '116.587922,40.081577'  # 华工五山校区
    #destination = '113.390579,23.065123'  # 中山大学东校区
    od_pair = generate_od_pair()
    origin_points = od_pair.keys()

    for origin_point in origin_points:
        # 获取当前时间
        now = datetime.now()        # 提取时、分、秒
        current = now.strftime("%Y-%m-%d %H:%M:%S")
        origin=f'{origin_point[1]},{origin_point[0]}'
        destination_points=od_pair[origin_point]
        for destination_point in destination_points:
            destination=f'{destination_point[1]},{destination_point[0]}'
            # print(origin,destination)
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
            #print(data)
            with open("data.json", "a", encoding="utf-8") as file:
                json.dump(obj=data, fp=file, ensure_ascii=False)#保留中文字符
                file.write(",\n")
        time.sleep(random.randint(1,3))
if __name__=='__main__':
    generate_data()
