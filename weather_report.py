import os
import requests
from datetime import datetime, timedelta

# 從 Secrets 讀取 Key
SERVER_JANG_KEY = os.getenv("SERVER_JANG_KEY")
WECOM_ROBOT_KEY = os.getenv("WECOM_ROBOT_KEY")

# 定義城市座標 (Open-Meteo 使用經緯度最準確)
CITIES = [
    {"name": "上海", "lat": 31.23, "lon": 121.47},
    {"name": "東營", "lat": 37.46, "lon": 118.49},
    {"name": "台北", "lat": 25.03, "lon": 121.56},
    {"name": "台南", "lat": 22.99, "lon": 120.21},
    {"name": "屏東", "lat": 22.67, "lon": 120.48},
    {"name": "東京", "lat": 35.68, "lon": 139.65},
    {"name": "首爾", "lat": 37.56, "lon": 126.97}
]

# 天氣代碼對應表 (WMO Code)
WMO_CODES = {
    0: "☀️ 晴朗", 1: "🌤️ 晴時多雲", 2: "⛅ 多雲", 3: "☁️ 陰天",
    45: "🌫️ 有霧", 48: "🌫️ 霧淞",
    51: "🌦️ 輕微毛毛雨", 53: "🌦️ 毛毛雨", 55: "🌧️ 密集毛毛雨",
    61: "🌧️ 輕微降雨", 63: "🌧️ 降雨", 65: "⛈️ 強降雨",
    71: "❄️ 輕微降雪", 73: "❄️ 降雪", 75: "❄️ 強降雪",
    80: "🌦️ 陣雨", 81: "🌧️ 強烈陣雨", 82: "⛈️ 極端陣雨",
    95: "⛈️ 雷陣雨", 96: "⛈️ 伴隨冰雹的雷雨"
}

def get_weather():
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    report = f"### 📅 明日天氣預報 ({tomorrow_date})\n\n"
    
    for city in CITIES:
        # 呼叫 Open-Meteo API
        url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
        
        try:
            res = requests.get(url, timeout=10).json()
            daily = res['daily']
            # 取得明天的索引 (通常是索引 1)
            idx = 1 
            
            code = daily['weathercode'][idx]
            max_t = daily['temperature_2m_max'][idx]
            min_t = daily['temperature_2m_min'][idx]
            desc = WMO_CODES.get(code, "未知天氣")
            
            # 下雨提醒邏輯 (代碼大於 50 通常代表有降水)
            rain_warning = ""
            if code >= 51:
                rain_warning = " ⚠️ **明日有雨，記得帶傘！**"

            report += f"* **{city['name']}**\n"
            report += f"  🌡️ 氣溫: {min_t}°C ~ {max_t}°C\n"
            report += f"  🌦️ 狀況: {desc}{rain_warning}\n\n"
            
        except Exception as e:
            report += f"* **{city['name']}** 數據獲取失敗 (Error: {str(e)})\n\n"
            
    return report

def send_push(content):
    # 1. Server醬 推播
    if SERVER_JANG_KEY:
        requests.post(f"https://sctapi.ftqq.com/{SERVER_JANG_KEY}.send", 
                      data={"title": "明日各城市氣象預報", "desp": content})
    
    # 2. 企業微信機器人 推播
    if WECOM_ROBOT_KEY:
        wecom_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECOM_ROBOT_KEY}"
        requests.post(wecom_url, json={
            "msgtype": "markdown",
            "markdown": {"content": content}
        })

if __name__ == "__main__":
    weather_info = get_weather()
    send_push(weather_info)
