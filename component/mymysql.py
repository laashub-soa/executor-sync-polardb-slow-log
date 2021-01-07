from contextlib import closing

import pymysql
from DBUtils.PooledDB import PooledDB

from component import mymysql
from exception import MyServiceException

db_pool = None
"""
https://webwareforpython.github.io/DBUtils/main.html
"""


def init(mysql_config):
    if not db_pool:
        mysql_config["cursorclass"] = pymysql.cursors.DictCursor
        mymysql.db_pool = PooledDB(pymysql, **mysql_config)


def execute(sql, parameters=None, is_batch_insert=False):
    execute_result = None
    if not parameters:
        parameters = {}
    try:
        with closing(mymysql.db_pool.connection()) as conn:
            with closing(conn.cursor()) as cursor:
                if is_batch_insert:
                    cursor.executemany(sql, parameters)
                else:
                    cursor.execute(sql, parameters)
                    # consider it INSERT or other
                    if sql.strip()[:len("INSERT")].upper() == "INSERT":
                        execute_result = cursor.lastrowid
                    else:
                        execute_result = cursor.fetchall()
                conn.commit()
    except Exception as e:
        raise MyServiceException("execute sql error: " + str(e))
    return execute_result


def extra_sql_content_2_template(sql_content):
    """
    抽取SQL内容为SQL模板
    :param sql_content: SQL内容
    :return:
    """
    sql_template = sql_content
    """
    抽取SQL模板的思路: 
    替换
        > < = ! 
            'xxx'   -> ?
            数字    -> ?  
            ()      -> 
        in (xxx)  -> in(?)
    """



    return sql_template
