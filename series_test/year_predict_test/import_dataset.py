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

cur.execute("drop table if exists year_predict_test;")
cur.execute("create table year_predict_test ( \
                data mvec, \
                res float4 \
            );")

pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FILENAME = pre_path + "/data/series/yead_predict/YearPredictionMSD.csv"

dataframe = pd.read_csv(DATA_FILENAME)

# 选择所有以'value'开头的列
value_columns = dataframe.columns[1:91]


# 遍历DataFrame的每一行，并将value列的值组装成列表形式的字符串
formatted_rows = []
for index, row in dataframe.iterrows():
    # 从当前行中提取value列的值
    values = row[value_columns].tolist()
    # 将值列表转换为字符串形式
    values_str = '[' + ', '.join(str(value) for value in values) + ']'
    # 将结果添加到列表中
    cur.execute("insert into year_predict_test values('{}', {} );".format(values_str+'{1,90}', row['value0']))
    if(index % 10 == 0):
        conn.commit()



## origin table test
value_columns = value_columns.insert(0, 'value0')
data_types = ['float4' for _ in value_columns] 

cur.execute("drop table if exists year_predict_origin_test;")
create_table_sql = 'create table year_predict_origin_test (\n  '
for i, column in enumerate(value_columns):
    create_table_sql += f"\"{column}\" {data_types[i]},\n"
create_table_sql = create_table_sql.rstrip(',\n') + '\n);'
cur.execute(create_table_sql)

cur.execute("copy year_predict_origin_test FROM '{}' WITH (FORMAT csv, HEADER true, DELIMITER ',');".format(DATA_FILENAME))
conn.commit()

conn.close()
# # 打印结果列表
# for row in formatted_rows:
#     print(row)