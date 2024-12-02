'''
Author: laihuihang laihuihang@foxmail.com
Date: 2024-08-26 14:11:08
LastEditors: laihuihang laihuihang@foxmail.com
LastEditTime: 2024-08-26 16:02:52
FilePath: /morphingdb_test/image_test/evadb_image_test_new.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import evadb
import time
import json
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

IMAGE_COUNT_LIST = [100, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
IMAGE_TEST_FILE = 'result/evadb_cifar10_test.json'

cursor = evadb.connect().cursor()


query = cursor.query("""
    CREATE FUNCTION IF NOT EXISTS Resnet18Huggingface
    TYPE  HuggingFace
    TASK 'image-classification'
    MODEL 'microsoft/resnet-18'
""").df()

for count in IMAGE_COUNT_LIST:
    cursor = evadb.connect().cursor()
    start_time = time.time()
    sql = "SELECT Resnet18Huggingface(data) FROM CIFAR10 limit {};".format(count)
    res = cursor.query(sql).df()
    end_time = time.time()
    print("cost time:", end_time - start_time, "s") 

    try:
        with open(IMAGE_TEST_FILE, 'r') as f_image:
            # 尝试加载现有数据
            timing_data_image = json.load(f_image)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或内容不是有效的JSON，初始化为一个空列表
        timing_data_image = []

    timing_data_image.append({
        "count": count,
        "sql":sql,
        "total_time": end_time - start_time
    })
    # 写回文件
    with open(IMAGE_TEST_FILE, 'w') as f_image:
        json.dump(timing_data_image, f_image, indent=4)