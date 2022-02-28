# -*- coding: utf8 -*-
import base64
import hmac
import json
import time
import math
from hashlib import sha256
import requests
from vika import Vika


def main_handler(event, context):
    datasheet_id = "替换成你的 datasheetId"  # 这里放「日报管理」表的表格id
    view_id = "替换成你的 viewId"  # 这里放「日报管理」表中「昨日视图」的视图id
    vika = Vika("替换成你的 API Token")  # vika API token，填写自己的，注意保护好不要泄露

    # 飞书 Webhook 地址，请保管好此 webhook 地址。不要公布在 Github、博客等可公开查阅的网站上。地址泄露后可能被恶意调用发送垃圾信息
    url = "替换成你的飞书群 Webhook 地址"
    # 神奇表单的填写地址，用来给员工填写日报
    form_link = "替换成你的神奇表单链接（日报速记）"

    dst = vika.datasheet(datasheet_id)
    records = dst.records.all()

    timestamp = str(round(time.time()))
    secret = ""  # 可选：创建飞书机器人勾选“加签”选项时使用

    key = f'{timestamp}\n{secret}'
    key_enc = key.encode('utf-8')
    msg = ""
    msg_enc = msg.encode('utf-8')
    hmac_code = hmac.new(key_enc, msg_enc, digestmod=sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    print(timestamp)

    # 整理日期时间数据
    localtime = time.localtime()  # 当前时间
    format_time = time.strftime("%Y年%m月%d日", localtime)
    format_week = time.strftime("%W", localtime)
    format_year = time.strftime("%Y年", localtime)



    notice_content = [{
      "tag": "text",
      "text": "今天是" + format_time + "，Q" + str(math.ceil(int(format_week) / 52)) + "季度\n"
    }, {
      "tag": "text",
      "text": "今天是第" + format_week + "周，距离" + format_year + "结束，还有" + str(52 - int(format_week)) + "周，请开始记录你的昨日产出和今日计划吧～\n\n"
    }, {
      "tag": "text",
      "text": "【说明】\n填写日报，3~5条的清单体形式 \n\n"
    }, {
      "tag": "a",
      "text": "[📝日报填写链接]",
      "href": form_link
    }, {
      "tag": "text",
      "text": "\n\n【昨日回顾】\n"
    }]

    # 对拿到的维格表数据做整理
    for record in records:
      print(record.json()["填写人"]["name"])
      print("https://vika.cn/workbench/" + datasheet_id + "/" + view_id + "/" + record._id)
      notice_content.append({
        "tag": "text",
        "text": record.json()["填写人"]["name"]+" "
      })
      notice_content.append({
        "tag": "a",
        "text": "[🔗点击查看]\n",
        "href": "https://vika.cn/workbench/" + datasheet_id + "/" + view_id + "/" + record._id  # 神奇表单链接，用来给员工填写日报
      })

    print(notice_content)

    # 飞书信息构造体，在这里可以按自己想要的格式去修改
    payload_message = {
      "timestamp": timestamp,
      "sign": sign,
      "msg_type": "post",
      "content": {
        "post": {
          "zh_cn": {
            "title": "【日报填写提醒】",
            "content": [
              notice_content
            ]
          }
        }
      }
    }
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload_message))
    print(response.text)
