import argparse
import requests

WEATHER_DESC = {
    0: "晴", 1: "大致晴", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇",
    51: "毛毛雨（轻）", 53: "毛毛雨", 55: "毛毛雨（密）",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨（轻）", 81: "阵雨", 82: "阵雨（强）",
    95: "雷暴", 96: "雷暴+冰雹", 99: "雷暴+大冰雹",
}   # 解码表

def get_coords(city):
    # 发 geocoding 请求，params={"name": city, "count": 1}
    # 用 .get("results") 判空：没有就 return None
    # 有就 return (latitude, longitude)
    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(url, params={"name": city, "count": 1}, timeout=10)
    response.raise_for_status()

    results = response.json().get("results")
    if not results:
        return None

    location = results[0]
    return location["latitude"], location["longitude"]

def get_weather(lat, lon):
    # 发 forecast 请求，params 里带上 latitude、longitude、
    # current、daily、timezone
    # return r.json()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone": "America/Toronto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description="查天气小工具")
    parser.add_argument("city", help="城市名，如 Toronto")
    args = parser.parse_args()

    coords = get_coords(args.city)
    if coords is None:
        print("没找到城市：{}".format(args.city))
        return

    weather = get_weather(*coords)
    current = weather["current"]
    current_desc = WEATHER_DESC.get(current["weather_code"], "未知")
    print("{} 当前温度：{}°C，{}".format(args.city, current["temperature_2m"], current_desc))

    daily = weather["daily"]
    print("未来 3 天：")
    for i in range(min(3, len(daily["time"]))):
        description = WEATHER_DESC.get(daily["weather_code"][i], "未知")
        print(
            "{}：{}，最高 {}°C，最低 {}°C".format(
                daily["time"][i], description,
                daily["temperature_2m_max"][i], daily["temperature_2m_min"][i]
            )
        )

if __name__ == "__main__":
    main()
