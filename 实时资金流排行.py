# 保持热爱 奔赴山海

import requests
from datetime import datetime
import json

url = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1123032430484859845254_1732549775639&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

#
def get_datas(page):
    datas = []
    cnt = 0

    for i in range(page):
        params = {
            "cb": "jquery112309245886249999282 1733396772298",
            "fid": "f62",
            "po": "1",
            "pz": "50",
            "pn": "page",
            "np": i,
            "fltt": "2",
            "invt": "2",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
        }

        resp = requests.get(url, headers=headers, params=params)
        data = resp.text

        start_index = data.find('(') + 1
        end_index = data.rfind(')')
        json_str = data[start_index:end_index]

        parsed_data = json.loads(json_str)

        diff_list = parsed_data['data']['diff']

        for diff in diff_list:
            from collections import OrderedDict
            cnt += 1
            datas.append(OrderedDict([
                ("序号", cnt),
                ("代码", diff["f12"]),
                ("名称", diff["f14"]),
                ("最新价", diff["f2"]),
                ("今日涨跌幅", diff["f3"]),
                ("今日主力净流入", {
                    "净额": diff["f62"],
                    "净占比": diff["f184"],
                }),
                ("今日超大单净流入", {
                    "净额": diff["f66"],
                    "净占比": diff["f69"],
                }),
                ("今日大单净流入", {
                    "净额": diff["f72"],
                    "净占比": diff["f75"],
                }),
                ("今日中单净流入", {
                    "净额": diff["f78"],
                    "净占比": diff["f81"],
                }),
                ("今日小单净流入", {
                    "净额": diff["f84"],
                    "净占比": diff["f87"],
                }),
            ]))

    return datas


def get_time():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    time = {
        "current_time": current_time
    }
    return time


time = get_time()
data = get_datas(3) # 设置爬取页数，一页有50条信息

data_to_write = {
    "time": time,
    "data": data
}

json_data = json.dumps(data_to_write, ensure_ascii=False, indent=4)

with open('实时资金流排行.json', 'w', encoding='utf-8') as f:
    f.write(json_data)
