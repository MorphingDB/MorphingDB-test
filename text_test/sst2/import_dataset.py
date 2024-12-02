import psycopg2
import os
import pandas as pd

TEXT_COUNT_LIST = [10000]

TEXT_TABLE = 'nlp_test'

IMAGE_VECTOR_TABLE = 'nlp_vector_test'

pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data/text/sst2"
df = pd.read_csv(pre_path+'/data/train.tsv', sep='\t')
pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
spiece_model = pre_path + "/models/spiece.model.old"


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



# 创建表
cur.execute("create table if not exists " + TEXT_TABLE + " (comment text);")
cur.execute("create table if not exists " + IMAGE_VECTOR_TABLE + " (comment_vec mvec);")
conn.commit()

# 删除表中的行
cur.execute("delete from " + TEXT_TABLE + ";")
cur.execute("delete from " + IMAGE_VECTOR_TABLE + ";")
conn.commit()

inserted_count = 0
# 插入表
for index, row in df.iterrows():
    if inserted_count >= 10000:  # 检查是否已经插入了10000条数据
        break  # 如果已经插入了10000条数据，则退出循环
    sql_comment = f"INSERT INTO " + TEXT_TABLE + " (comment) VALUES ('{}')".format(row['sentence'].replace("'","''"))
    cur.execute(sql_comment)
    sql_vec = f"INSERT INTO " + IMAGE_VECTOR_TABLE + " (comment_vec) VALUES ({})".format("text_to_vector('{}', '{}')".format(spiece_model, row['sentence'].replace("'","''")))
    cur.execute(sql_vec)
    conn.commit()
    inserted_count += 1
conn.close()