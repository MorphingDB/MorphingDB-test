'''
Author: laihuihang laihuihang@foxmail.com
Date: 2024-08-11 22:55:23
LastEditors: laihuihang laihuihang@foxmail.com
LastEditTime: 2024-08-22 14:56:30
FilePath: /morphingdb_test/text_test/imdb/import_dataset.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import psycopg2
import os
import pandas as pd
import morphingdb
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification



tokenizer = AutoTokenizer.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

TEXT_COUNT_LIST = [10000]
TEXT_TABLE = 'financial_phrasebank_test'
TEXT_VECTOR_TABLE = 'financial_phrasebank_vector_test'




db_config = {
    "dbname": "postgres",
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "123456"
}


conn = psycopg2.connect(**db_config)
cur = conn.cursor()



# create table
cur.execute("create table if not exists " + TEXT_TABLE + " (comment text);")
cur.execute("create table if not exists " + TEXT_VECTOR_TABLE + " (comment_vec mvec);")
conn.commit()


cur.execute("delete from " + TEXT_TABLE + ";")
cur.execute("delete from " + TEXT_VECTOR_TABLE + ";")
conn.commit()

SENTENCE_LIST = []

pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data/text/financial_phrasebank"
TXT_LIST = [pre_path+'/data/Sentences_50Agree.txt', 
            pre_path+'/data/Sentences_66Agree.txt', 
            pre_path+'/data/Sentences_75Agree.txt', 
            pre_path+'/data/Sentences_AllAgree.txt']


# insert sentences
for txt in TXT_LIST:
    with open(txt, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            part_before_at = line.split('@')[0].strip()  
            SENTENCE_LIST.append(part_before_at)
            sql = f"INSERT INTO " + TEXT_TABLE + " (comment) VALUES ('{}')".format(part_before_at.replace("'","''"))
            cur.execute(sql)
            conn.commit()


# insert vectors
tensor = tokenizer(SENTENCE_LIST, padding=True, truncation=True, return_tensors="pt")
input_ids = tensor['input_ids']
attention_mask = tensor['attention_mask']
input_ids_list = [input_ids[i].unsqueeze(0) for i in range(input_ids.size(0))]
attention_mask_list = [attention_mask[i].unsqueeze(0) for i in range(attention_mask.size(0))]

for i in range(len(input_ids_list)):
    stack_tensor = torch.stack([input_ids_list[i], attention_mask_list[i]], 1)
    mvec_str = morphingdb.tensor_to_mvec(stack_tensor)
    sql = sql = f"INSERT INTO " + TEXT_VECTOR_TABLE + " (comment_vec) VALUES ('{}')".format(mvec_str)
    cur.execute(sql)
    conn.commit()
conn.close()