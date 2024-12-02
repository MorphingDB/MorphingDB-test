'''
Author: laihuihang laihuihang@foxmail.com
Date: 2024-08-08 13:52:21
LastEditors: laihuihang laihuihang@foxmail.com
LastEditTime: 2024-08-08 16:12:08
FilePath: /morphingdb_test/image_test/cifar10/import_dataset.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import psycopg2
import os
import evadb

IMAGE_COUNT_LIST = [1000]
pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
IMAGE_PRE_PATH = pre_path + '/data/image/cifar10/test/'
print(IMAGE_PRE_PATH)
IMAGE_TABLE = 'cifar_image_table'
IMAGE_VECTOR_TABLE = 'cifar_image_vector_table'

# 初始化一个空列表来存储所有文件的路径
image_names = []

# 使用os.walk遍历IMAGE_PRE_PATH及其所有子目录
for root, dirs, files in os.walk(IMAGE_PRE_PATH):
    for file in files:
        # 构建完整的文件路径
        full_path = os.path.join(root, file)
        # 将文件路径添加到列表中
        image_names.append(full_path)


# 配置数据库连接参数
db_config = {
    "dbname": "postgres",
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "123456"
}


# 连接MorphingDB数据库
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

# 创建表
cur.execute("create table if not exists " + IMAGE_TABLE  + " (id int, image_path text);")
cur.execute("create table if not exists " + IMAGE_VECTOR_TABLE  + " (id int, image_vector mvec);")
conn.commit()

# 删除表中的行
cur.execute("delete from " + IMAGE_TABLE + ";")
cur.execute("delete from " + IMAGE_VECTOR_TABLE + ";")
conn.commit()


# 插入表
for index in range(len(image_names)):
    sql = f"INSERT INTO " + IMAGE_TABLE + " (id, image_path) VALUES ({},'{}')".format(index+1, image_names[index])
    #print(sql)
    cur.execute(sql)
conn.commit()


for index in range(len(image_names)):
    sql = f"INSERT INTO " + IMAGE_VECTOR_TABLE + " (id, image_vector) VALUES ({},{})".format(index+1, "image_to_vector(224,224,0.4914,0.4822,0.4465,0.2023,0.1994,0.2010, '{}')".format(image_names[index]))
    #print(sql)
    cur.execute(sql)
conn.commit()
conn.close()




# 连接evadb
cursor = evadb.connect().cursor()
cursor.query("DROP TABLE IF EXISTS CIFAR10").df()
for index in range(len(image_names)):
    cursor.query("LOAD IMAGE '{}' INTO CIFAR10".format(image_names[index])).df()
