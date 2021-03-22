"""
一个案例数据:
{
    "msgtype": "text",
    "text": {
        "content": "告警测试exception"
    },
    "at": {
        "atMobiles": [
            "17607335040"
        ]
    }
}
参考文档: https://developers.dingtalk.com/document/app/custom-robot-access
"""
import json

import requests

base_url = "https://oapi.dingtalk.com/robot/send"


def request_dingding_webhook(access_token, title="", content="", at_mobiles=[]):
    request_data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": content
        },
        "at": {
            "atMobiles": at_mobiles,
            "isAtAll": False
        }
    }
    headers = {'content-type': 'application/json'}
    request_url = "%s?access_token=%s" % (base_url, access_token)
    resp = requests.post(request_url, data=json.dumps(request_data), headers=headers)
    return resp.text
