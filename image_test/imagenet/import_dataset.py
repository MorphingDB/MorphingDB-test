import psycopg2
import os
import evadb


IMAGE_COUNT_LIST = [10000]
pre_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
IMAGE_PRE_PATH = pre_path + '/data/image/image-net/data/'
IMAGE_TABLE = 'imagenet_table_'
IMAGE_VECTOR_TABLE = 'imagenet_vector_table_'


image_name = os.listdir(IMAGE_PRE_PATH)

# 配置数据库连接参数
db_config = {
    "dbname": "postgres",
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "123456"
}


def import_morphingdb_imagenet_dataset():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # 创建表
    for image_count in IMAGE_COUNT_LIST:
        cur.execute("create table if not exists " + IMAGE_TABLE + str(image_count) + " (id int, image_path text);")
        cur.execute("create table if not exists " + IMAGE_VECTOR_TABLE + str(image_count) + " (id int, image_vector mvec);")
        conn.commit()

    # 删除表中的行
    for image_count in IMAGE_COUNT_LIST:
        cur.execute("delete from " + IMAGE_TABLE + str(image_count) + ";")
        cur.execute("delete from " + IMAGE_VECTOR_TABLE + str(image_count) + ";")
        conn.commit()

    # 插入表
    for image_count in IMAGE_COUNT_LIST:
        for index in range(image_count):
            sql = f"INSERT INTO " + IMAGE_TABLE + str(image_count) + " (id, image_path) VALUES ({},'{}')".format(index+1, IMAGE_PRE_PATH+image_name[index])
            #print(sql)
            cur.execute(sql)
        conn.commit()

    for image_count in IMAGE_COUNT_LIST:
        for index in range(image_count):
            sql = f"INSERT INTO " + IMAGE_VECTOR_TABLE + str(image_count) + " (id, image_vector) VALUES ({},{})".format(index+1, "image_to_vector(224,224,0.4914,0.4822,0.4465,0.2023,0.1994,0.2010, '{}')".format(IMAGE_PRE_PATH+image_name[index]))
            #print(sql)
            cur.execute(sql)
        conn.commit()

    conn.close()


def import_evadb_imagenet_dataset():
    # 连接evadb
    cursor = evadb.connect().cursor()
    cursor.query("DROP TABLE IF EXISTS IMAGENET").df()
    for index in range(len(image_name)):
        cursor.query("LOAD IMAGE '{}' INTO IMAGENET".format(IMAGE_PRE_PATH+image_name[index])).df()
    


if __name__ == "__main__":
    import_morphingdb_imagenet_dataset()
    import_evadb_imagenet_dataset()

