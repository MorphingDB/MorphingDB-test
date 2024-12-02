'''
Descripttion: 
version: 
Author: LHH
Date: 2024-07-06 21:05:22
LastEditors: LHH
LastEditTime: 2024-07-06 21:33:52
'''
import pandas as pd
import psycopg2
import os


db_config = {
    "dbname": "postgres",
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "123456"
}

# 连接数据库
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

# cur.execute("drop table if exists swarm_test;")
# cur.execute("create table swarm_test ( \
#                 data mvec, \
#                 res float4 \
#             );")


pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FILENAME = pre_path + "/data/series/swarm/Swarm_Behaviour.csv"

dataframe = pd.read_csv(DATA_FILENAME)


# 选择所有以'value'开头的列
value_columns = dataframe.columns[:-1]


cur.execute("drop table if exists swarm_test;")
# 遍历DataFrame的每一行，并将value列的值组装成列表形式的字符串
create_mvec_sql = 'CREATE TABLE swarm_test ( \
                        data  mvec,\
                        flag  FLOAT4 \
                    );'
cur.execute(create_mvec_sql)
formatted_rows = []
for index, row in dataframe.iterrows():
    # 从当前行中提取value列的值
    values = row[value_columns].tolist()
    # 将值列表转换为字符串形式
    values_str = '[' + ', '.join(str(value) for value in values) + ']'
    # 将结果添加到列表中
    cur.execute("insert into swarm_test values('{}', {} );".format(values_str+'{1,2400}', row['Swarm_Behaviour']))
    if(index % 10 == 0):
        conn.commit()



## origin table test
# value_columns.append('reference')
# data_types = ['float4' for _ in value_columns] 

cur.execute("drop table if exists swarm_origin_test;")
create_table_sql = 'CREATE TABLE swarm_origin_test ( \
                        data  FLOAT4[],\
                        flag  FLOAT4 \
                    );'
cur.execute(create_table_sql)
for index, row in dataframe.iterrows():
    # 从当前行中提取value列的值
    values = row[value_columns].tolist()
    # 将值列表转换为字符串形式
    values_str = '{' + ', '.join(str(value) for value in values) + '}'
    # 将结果添加到列表中
    cur.execute("insert into swarm_origin_test values('{}', {} );".format(values_str, row['Swarm_Behaviour']))
    if(index % 10 == 0):
        conn.commit()


conn.close()
