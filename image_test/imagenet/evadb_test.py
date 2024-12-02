import evadb
import time
import json

IMAGE_COUNT_LIST = [100, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
IMAGE_TEST_FILE = 'result/evadb_imagenet_test.json'

cursor = evadb.connect().cursor()



query = cursor.query("""
    CREATE FUNCTION IF NOT EXISTS Resnet18Test
    INPUT  (data NDARRAY (3, 500, 375))
    OUTPUT (labels NDARRAY FLOAT32(3))
    TYPE  Classification
    IMPL  'evadb_resnet18.py';
""").df()

for count in IMAGE_COUNT_LIST:
    start_time = time.time()
    sql = """SELECT Resnet18Test(data)  FROM IMAGENET limit {};""".format(count)
    res = cursor.query(sql).df()
    end_time = time.time()
    print("cost time:", end_time - start_time, "s") 

    try:
        with open(IMAGE_TEST_FILE, 'r') as f_image:
            # 加载现有数据
            timing_data_image = json.load(f_image)

        # 遍历列表
        for item in timing_data_image:
            # 查找count为100且total_time与scan_time都为零的项
            if item["count"] == count and item["total_time"] == 0 and item["scan_time"] == 0:
                # 修改total_time和scan_time
                item["total_time"] = end_time - start_time
                item["scan_time"] = (end_time - start_time) - item['load_model_time'] - item['pre_time'] - item['infer_time'] - item['post_time']
                # 由于找到了需要的项，可以结束循环
                item["sql"] = sql
                break
        
        print(timing_data_image)
        # 将更新后的列表写回文件
        with open(IMAGE_TEST_FILE, 'w') as f_image:
            json.dump(timing_data_image, f_image, indent=4)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"An error occurred: {e}")