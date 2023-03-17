# -*- coding: UTF-8 -*-
import requests, os, time, json

cookie = os.environ["GLA_COOKIE"]
robot = os.environ["WECOM_ROBOT"]

UNIT = 1024
UNIT_B = 'B'
UNIT_KB = 'KB'
UNIT_MB = 'MB'
UNIT_GB = 'GB'
UNIT_TB = 'TB'
ONE_B = 1
ONE_KB = ONE_B * UNIT
ONE_MB = ONE_KB * UNIT
ONE_GB = ONE_MB * UNIT
ONE_TB = ONE_GB * UNIT
TEN_B = 10 * ONE_B
TEN_KB = 10 * TEN_B
TEN_MB = 10 * ONE_MB
TEN_GB = 10 * ONE_GB
TEN_TB = 10 * ONE_TB

GRACE_LIST = [
    (TEN_TB, ONE_TB, UNIT_TB),
    (TEN_GB, ONE_GB, UNIT_GB),
    (TEN_MB, ONE_MB, UNIT_MB),
    (TEN_KB, ONE_KB, UNIT_KB),
    (TEN_B, ONE_B, UNIT_B),
]


def glados_checkin():
    # url_home = 'https://glados.rocks/console'
    url_checkin = "https://glados.rocks/api/user/checkin"
    url_status = "https://glados.rocks/api/user/status"
    url_traffic = "https://glados.rocks/api/user/traffic"
    payload = {
        'token': 'glados.network'
    }

    headers = {
        'referer': 'https://glados.rocks/console/checkin',
        'origin': 'https://glados.rocks',
        'authority': 'glados.rocks',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'authorization': '72598693918590856276242251790070-900-1440',
        'content-type': 'application/json;charset=UTF-8',
        'cache-control': 'max-age=0',
        'cookie': cookie,
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    resp_checkin = requests.post(url_checkin, headers=headers, json=payload)
    # print(f'resp_checkin: {resp_checkin}, {resp_checkin.content}')
    resp_status = requests.get(url_status, headers=headers)
    # print(f'resp_status: {resp_status}, {resp_status.content}')
    resp_traffic = requests.get(url_traffic, headers=headers)
    # print(f'resp_traffic: {resp_traffic}, {resp_traffic.content}')
    used_today = resp_traffic.json().get('data', {}).get('today')
    unit = UNIT_B
    if used_today:
        used_today = float(used_today)
        for one in GRACE_LIST:
            if used_today >= one[0]:
                used_today /= one[1]
                unit = one[2]
                break
    if 'message' in resp_checkin.text:
        msg_checkin = resp_checkin.json().get('message')
        if msg_checkin == 'Please Try Tomorrow':
            print('已经签到成功，无需重复签到')
        data_status = resp_status.json().get('data', {})
        left_days = data_status.get('leftDays')
        email = data_status.get('email')
        info = f'> 签到时间：{time.strftime("%Y-%m-%d %H:%M:%S")}\n' \
               f'> 签到项目：[GlaDOS]-[checkin]\n' \
               f'> 签到账号：{email}\n' \
               f'> 签到信息：{msg_checkin}\n' \
               f'- 当前套餐：Edu Plan\n' \
               f'- 套餐流量：30 GB.\n' \
               f'- 剩余天数：{float(left_days):.0f}\n' \
               f'- 已用流量：{float(used_today):.2f} {unit}\n'
    else:
        info = f'可能是Cookie过期了，请联系管理员处理'
    return info


def wecom_send(content):
    if not robot:
        raise Exception('未指定机器人，无法处理发送请求')
    url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send'
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'key': robot
    }
    data = json.dumps({
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": ["@all"],
            # "mentioned_mobile_list": ["@all"]
        }
    })
    resp = requests.post(url, params=params, headers=headers, json=data)
    if resp.status_code == requests.codes.ok:
        resp_data = resp.json()
        errcode = resp_data.get('errcode')
        errmsg = resp_data.get('errmsg')
        if errcode == 0 and errmsg == 'ok':
            return
        raise Exception(f'[{errcode}]{errmsg}')
    raise Exception(f'[{resp.status_code}]{resp.reason}')


def main():
    info = glados_checkin()
    print(info)
    wecom_send(info)


if __name__ == '__main__':
    main()
