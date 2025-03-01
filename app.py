from flask import Flask, request
import requests
import hashlib
import xml.etree.ElementTree as ET
import time
import os

app = Flask(__name__)

# 从环境变量获取配置
WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'default_token')
QWEATHER_KEY = os.environ.get('QWEATHER_KEY', 'default_key')

# 验证微信签名
def check_signature(signature, timestamp, nonce):
    tmp = [WECHAT_TOKEN, timestamp, nonce]
    tmp.sort()
    tmp = ''.join(tmp).encode('utf-8')
    return hashlib.sha1(tmp).hexdigest() == signature

# 获取天气数据（中文）
def get_weather(city):
    url = f"https://free-API.qweather.com/v7/weather/now?location={city}&key={QWEATHER_KEY}&lang=zh"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] == "200":
            now = data["now"]
            return f"{city} 当前天气：{now['text']}，温度：{now['temp']}°C，湿度：{now['humidity']}%"
        else:
            return "获取天气数据失败，请稍后重试"
    except:
        return "天气服务不可用"

# 微信消息处理
@app.route('/', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        if check_signature(signature, timestamp, nonce):
            return echostr
        return "验证失败"
    elif request.method == 'POST':
        try:
            root = ET.fromstring(request.data)
            msg_type = root.find('MsgType').text
            from_user = root.find('FromUserName').text
            to_user = root.find('ToUserName').text
            if msg_type == 'text':
                content = root.find('Content').text
                weather_info = get_weather(content)
                reply = f"""<xml>
                    <ToUserName><![CDATA[{from_user}]]></ToUserName>
                    <FromUserName><![CDATA[{to_user}]]></FromUserName>
                    <CreateTime>{int(time.time())}</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[{weather_info}]]></Content>
                </xml>"""
                return reply
            else:
                return "success"
        except:
            return "success"
    return ''

# UptimeRobot ping 路由
@app.route('/ping', methods=['GET'])
def ping():
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)