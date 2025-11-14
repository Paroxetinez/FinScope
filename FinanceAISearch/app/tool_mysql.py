import pymysql
import sqlite3
import os
# def execute_sql(sql,  is_query=True):
#     db_config = {
#         'engine': 'sqlite',  # 或 'sqlite'
#         'database': 'users.db'  # SQLite 数据库文件的路径
#         # 'host': '39.99.237.144',
#         # 'user': 'root',
#         # 'password': '',
#         # 'database': 'Ai'
#         # 'engine': 'mysql',  # 或 'sqlite'
#         # 'host': 'sh-cdb-jsxfa24s.sql.tencentcdb.com',
#         # 'user': 'root',
#         # 'password': '',
#         # 'database': 'finance'
#     }
#     """
#     执行SQL语句，如果是查询则返回查询结果列表，如果是更新或插入则返回操作状态。

#     :param sql: SQL语句
#     :param db_config: 数据库配置信息字典，包含host, user, password, database等
#     :param is_query: 布尔值，指示是否为查询操作
#     :return: 查询结果列表（字典形式）或操作状态（布尔值）
#     """
#     if 'sqlite' in db_config.get('engine', '').lower():
#         conn = sqlite3.connect(db_config['database'])
#     else:
#         conn = pymysql.connect(
#             host=db_config['host'],
#             user=db_config['user'],
#             password=db_config['password'],
#             database=db_config['database']
#         )

#     try:
#         with conn.cursor() as cursor:
#             # Execute SQL
#             cursor.execute(sql)

#             if is_query:
#                 # Fetch all rows from the last executed statement using a dictionary cursor
#                 columns = [col[0] for col in cursor.description]
#                 results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#                 return results
#             else:
#                 # Commit changes for INSERT, UPDATE, DELETE operations
#                 conn.commit()
#                 return True
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         conn.rollback()
#         return False
#     finally:
#         conn.close()


def execute_sql(sql, params=None, is_query=True):
    db_config = {
        'engine': 'sqlite',
        'database': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'users.db')
    }

    if db_config.get('engine', '').lower() != 'sqlite':
        raise ValueError("Unsupported database engine")

    conn = None
    try:
        conn = sqlite3.connect(db_config['database'])
        conn.row_factory = sqlite3.Row  # 这样可以通过列名访问结果

        with conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if is_query:
                rows = cursor.fetchall()
                # 将 sqlite3.Row 对象转换为字典
                return [dict(row) for row in rows]
            else:
                conn.commit()
                return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False if is_query else False

    finally:
        if conn:
            conn.close()

# 示例用法
# db_config = {
#     'engine': 'mysql',  # 或 'sqlite'
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'your_password',
#     'database': 'your_database'
# }

# 查询示例
# query_sql = "SELECT * FROM your_table"
# result = execute_sql(query_sql,  is_query=True)
# print(result)
#
# # 更新或插入示例
# update_sql = "UPDATE your_table SET column_name = 'value' WHERE condition = 'value'"
# status = execute_sql(update_sql, is_query=False)
# print(status)
