import os
import requests
from datetime import datetime, timedelta

# 從環境變數讀取 Key (安全考量)
SERVER_JANG_KEY = os.getenv("SERVER_JANG_KEY")
WECOM_ROBOT_KEY = os.getenv("WECOM_ROBOT_KEY")

CITIES = ["Shanghai", "Dongying", "Taipei", "Tainan", "Pingtung", "Tokyo", "Seoul"]
CITY_NAMES = ["上海", "東營", "台北", "台南", "屏東", "東京", "首爾"]

def get_weather():
    report = f"### 📅 明日天氣預報 ({datetime.now().year}-{(datetime.now()+timedelta(days=1)).strftime('%m-%d')})\n\n"
    
    for i, city in enumerate(CITIES):
        # 使用 wttr.in 獲取數據 (免註冊 API，適合快速部署)
        url = f"https://wttr.in/{city}?format=j1"
        try:
            res = requests.get(url).json()
            tomorrow = res['weather'][1]
            max_t = tomorrow['maxtempC']
            min_t = tomorrow['mintempC']
            desc = tomorrow['hourly'][4]['lang_zh_tw'][0]['value'] # 取中午時段描述
            
            # 圖示與下雨提醒
            icon = "☀️"
            rain_warning = ""
            if "雨" in desc:
                icon = "🌧️"
                rain_warning = " ⚠️ **請務必帶傘！**"
            elif "雲" in desc or "陰" in desc:
                icon = "☁️"

            report += f"* **{CITY_NAMES[i]}** {icon}\n"
            report += f"  🌡️ 氣溫: {min_t}°C ~ {max_t}°C\n"
            report += f"  🌦️ 狀況: {desc}{rain_warning}\n\n"
        except:
            report += f"* **{CITY_NAMES[i]}** 數據獲取失敗\n\n"
    return report

def send_push(content):
    # 1. Server醬 推播
    requests.post(f"https://sctapi.ftqq.com/{SERVER_JANG_KEY}.send", 
                  data={"title": "明日氣象提醒", "desp": content})
    
    # 2. 企業微信機器人 推播
    wecom_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECOM_ROBOT_KEY}"
    requests.post(wecom_url, json={
        "msgtype": "markdown",
        "markdown": {"content": content}
    })

if __name__ == "__main__":
    weather_info = get_weather()
    send_push(weather_info)
