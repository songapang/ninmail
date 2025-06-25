"""使用requests请求代理服务器
请求http和https网页均适用
"""

import requests
import random
import json


def get_proxy():
    page_url = "https://dev.kdlapi.com/testproxy"  # 要访问的目标网页
    # API接口，返回格式为json
    api_url = "https://dps.kdlapi.com/api/getdps/?secret_id=o7bor5v8vj5ajykckb6u&signature=a7y4let9do95hd3kve0hkmxtpldmc0oe&num=10&pt=1&sep=1"
    
    response = requests.get(api_url)
    proxy_list = response.text.strip().split('\r\n')  # 将响应文本分割成数组
    
    # 随机选择一个代理
    proxy_ip = random.choice(proxy_list)
    # 用户名密码认证(私密代理/独享代理)
    username = "d1275933638"
    password = "rddyw064"

    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
    }

    headers = {
    "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
    }
    r = requests.get(page_url, proxies=proxies, headers=headers)
    print(r.status_code)  # 获取Response的返回码

    if r.status_code == 200:
        r.enconding = "utf-8"  # 设置返回内容的编码
        print(r.content)  # 获取页面内容
    return proxies['http']
