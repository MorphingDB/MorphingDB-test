'''
Author: laihuihang laihuihang@foxmail.com
Date: 2024-08-08 17:11:46
LastEditors: laihuihang laihuihang@foxmail.com
LastEditTime: 2024-08-09 14:50:17
FilePath: /morphingdb_test/image_test/cifar10/evadb_test.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import evadb
import time
import json

IMAGE_COUNT_LIST = [100, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
IMAGE_TEST_FILE = 'result/evadb_stanford_dogs_test.json'

cursor = evadb.connect().cursor()



query = cursor.query("""
    CREATE FUNCTION IF NOT EXISTS AlexnetStanford
    INPUT  (data NDARRAY FLOAT32(ANYDIM))
    OUTPUT (labels NDARRAY FLOAT32(10))
    TYPE  Classification
    IMPL  'evadb_alexnet_stanford_dog.py';
""").df()

for count in IMAGE_COUNT_LIST:
    start_time = time.time()
    res = cursor.query("""
        SELECT AlexnetStanford(data)
        FROM STANFORD limit {};
    """.format(count)).df()
    end_time = time.time()
    print("cost time:", end_time - start_time, "s") 

    try:
        with open(IMAGE_TEST_FILE, 'r') as f_image:
            # 加载现有数据
            timing_data_image = json.load(f_image)

        # 遍历列表
        for item in timing_data_image:
            # 查找count为100且total_time与scan_time都为零的项
            print(item)
            if item["count"] == count and item["total_time"] == 0 and item["scan_time"] == 0:
                # 修改total_time和scan_time
                item["total_time"] = end_time - start_time
                item["scan_time"] = (end_time - start_time) - item['load_model_time'] - item['pre_time'] - item['infer_time'] - item['post_time']
                # 由于找到了需要的项，可以结束循环
                break
        
        print(timing_data_image)
        # 将更新后的列表写回文件
        with open(IMAGE_TEST_FILE, 'w') as f_image:
            json.dump(timing_data_image, f_image, indent=4)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"An error occurred: {e}")