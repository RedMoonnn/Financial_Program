from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import time
import requests
from source_data_1 import *
from save_to_database_1 import *
from save_to_minio import *
from visualize_1 import visualize_data

app = Flask(__name__)
CORS(app)

def web_crawler(flow_id, market_filter, day_filter, pages, day_name, process_func_id):
    """爬虫主体函数"""
    results = []
    counter = 0

    for i in range(int(pages)):
        params = BASE_PARAMS.copy()
        params.update({
            "cb": flows_id[flow_id - 1],
            "fid": day_filter,
            "pn": str(i + 1),  # 当前页码
            "fs": market_filter,
            "fields": fields_ids[process_func_id]
        })

        response = requests.get(url, headers=headers, params=params)
        data = response.text

        # 清洗爬取数据，除去原数据标识头
        start_index = data.find('(') + 1
        end_index = data.rfind(')')
        json_str = data[start_index:end_index]

        parsed_data = json.loads(json_str)
        diff_list = parsed_data['data']['diff']

        for diff in diff_list:
            counter += 1
            results.append(process_diff[process_func_id](diff, counter, flow_id, day_name))

    return results

def get_current_time():
    """获取当前时间"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/api/fetch-data', methods=['POST'])
def fetch_data():
    try:
        # 记录开始运行时间
        start_time = time.time()

        data = request.json
        flow_choice = int(data.get('flowType', 1))
        
        if flow_choice == 1:
            market_choice = int(data.get('marketType', 1))
            market_filter = market_ids[market_choice - 1]
            
            day_choice = int(data.get('timeRange', 1))
            day_filter = day1_ids[day_choice - 1]
            day_name = day1_names[day_choice - 1].split("_Ranking")[0]
            
            process_func_id = day_choice - 1
            pages = data.get('pages', 1)
            
            data_results = web_crawler(flow_choice, market_filter, day_filter, pages, day_name, process_func_id)
            
            title = f"{flows_names[flow_choice - 1]}-{market_names[market_choice - 1]}-{day_name}"
            
        elif flow_choice == 2:
            detail_choice = int(data.get('marketType', 1))
            detail_filter = detail_flows_ids[detail_choice - 1]
            
            day_choice = int(data.get('timeRange', 1))
            day_filter = day2_ids[day_choice - 1]
            day_name = day2_names[day_choice - 1].split("_Ranking")[0]
            
            process_func_id = [0, 2, 3][day_choice - 1]
            pages = data.get('pages', 1)
            
            data_results = web_crawler(flow_choice, detail_filter, day_filter, pages, day_name, process_func_id)
            
            title = f"{flows_names[flow_choice - 1]}-{detail_flows_names[detail_choice - 1]}-{day_name}"
        
        current_time = get_current_time()
        
        # 文件存储
        output_data = {
            "time": current_time,
            "title": title,
            "data": data_results
        }
        
        # 存储文件
        file_name = f"{title}.json"
        os.makedirs(f'./data/{title}', exist_ok=True)
        
        with open(f'./data/{title}/{file_name}', 'w', encoding='utf-8') as file:
            json.dump(output_data, file, ensure_ascii=False, indent=4)

        end_time = time.time() - start_time
        # print(f"{file_name} has been successfully generated.")
        print(f"Main\t: {end_time} seconds")

        # 调用绘图函数
        visualize_data(title, day_name, pages)

        # 调用存储函数,存储至mysql
        store_data_to_db(data_results, title, day_name)
        
        # 调用存储函数,存储至MinIO
        store_data_to_minio(title)
        
        # return jsonify(output_data), 200
        return jsonify({"message": "successful!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True) 