import evadb
import time
import json

TEXT_COUNT_LIST = [100, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
TEXT_TEST_FILE = 'result/evadb_test.json'

cursor = evadb.connect().cursor()

query = cursor.query("""
    DROP DATABASE IF EXISTS postgres_data;
""").df()
query = cursor.query("""
    CREATE DATABASE IF NOT EXISTS postgres_data
    WITH ENGINE = 'postgres',
    PARAMETERS = {
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"
    }
""").df()

# query = cursor.query("""
#     DROP FUNCTION IMDBTest;
# """).df()

query = cursor.query("""
    CREATE FUNCTION IF NOT EXISTS IMDBTest
    INPUT  (question TEXT)
    OUTPUT (labels NDARRAY FLOAT32(3))
    TYPE  Classification
    IMPL  'evadb_imdb.py';
""").df()

for count in TEXT_COUNT_LIST:
    start_time = time.time()
    sql = "SELECT IMDBTest(comment) FROM postgres_data.imdb_test limit {};".format(count)
    res = cursor.query(sql).df()
    print(res)
    end_time = time.time()
    print("cost time:", end_time - start_time, "s") 

    try:
        with open(TEXT_TEST_FILE, 'r') as f_image:
            # 加载现有数据
            timing_data_image = json.load(f_image)

        # 遍历列表
        for item in timing_data_image:
            # 查找count为100且total_time与scan_time都为零的项
            if item["count"] == count and item["total_time"] == 0 and item["scan_time"] == 0:
                # 修改total_time和scan_time
                item["sql"] = sql
                item["total_time"] = end_time - start_time
                item["scan_time"] = (end_time - start_time) - item['load_model_time'] - item['pre_time'] - item['infer_time'] - item['post_time']
                # 由于找到了需要的项，可以结束循环
                break
        
        print("timing_data_image", timing_data_image)
        # 将更新后的列表写回文件
        with open(TEXT_TEST_FILE, 'w') as f_image:
            json.dump(timing_data_image, f_image, indent=4)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"An error occurred: {e}")