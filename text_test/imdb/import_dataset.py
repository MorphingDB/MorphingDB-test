import psycopg2
import os
import pandas as pd

TEXT_COUNT_LIST = [10000]

TEXT_TABLE = 'imdb_test'

IMAGE_VECTOR_TABLE = 'imdb_vector_test'


pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data/text/imdb"
df = pd.read_parquet(pre_path+"/data/test-00000-of-00001.parquet")

pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
spiece_model = pre_path + "/models/spiece.model.old"

# from transformers import AutoTokenizer, AutoModelWithLMHead

# tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-imdb-sentiment")

# model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-imdb-sentiment")
# input_ids = tokenizer.encode(df.iloc[0,0] + '</s>', return_tensors='pt')
# print(input_ids)


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
# cur.execute("delete from " + TEXT_TABLE + ";")
cur.execute("delete from " + IMAGE_VECTOR_TABLE + ";")
conn.commit()

inserted_count = 0
#插入表
for index, row in df.iterrows():
    if inserted_count >= 10000:  # 检查是否已经插入了10000条数据
        break  # 如果已经插入了10000条数据，则退出循环
    sql_comment = f"INSERT INTO " + TEXT_TABLE + " (comment) VALUES ('{}')".format(row['text'].replace("'","''"))
    cur.execute(sql_comment)
    sql_vec = f"INSERT INTO " + IMAGE_VECTOR_TABLE + " (comment_vec) VALUES ({})".format("text_to_vector('{}','{}')".format(spiece_model, df.iloc[index,0].replace("'","''")))
    cur.execute(sql_vec)
    conn.commit()

conn.close()