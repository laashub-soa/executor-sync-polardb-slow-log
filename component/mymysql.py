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


def extra_sql_template(sql_content):
    """
    抽取SQL模板(指纹)
    :param sql_content: SQL内容
    :return:
    """
    """
    抽取SQL模板的思路: 
    替换
        > < = ! 
            'xxx'                        -> ?
            特殊字符+数字开头的+特殊字符   -> 特殊字符+?+特殊字符  
        in (xxx)                         -> in(?)
    """
    print("=" * 200)
    print("sql_content: %s" % sql_content)
    sql_template = ''
    is_quote_start = False  # 是否开始引号
    is_digit_start = False  # 是否开始数字
    last_sql_content_item = ''
    for item in sql_content:
        # 从字符串中抽取引号部分为模板
        if item == '\'':
            is_quote_start = not is_quote_start
            if not is_quote_start:
                sql_template += '?'
            continue
        if is_quote_start:
            continue
        # 从字符串中抽取数字部分为模板
        if item.isdigit():
            if not last_sql_content_item.isdigit() and not last_sql_content_item.isalpha():
                is_digit_start = True
        else:
            if is_digit_start:
                is_digit_start = False
                sql_template += '?'
        if is_digit_start:
            continue
        sql_template += item
        last_sql_content_item = item
    if is_digit_start:
        sql_template += '?'
    # 从字符串中抽取in()部分中多个模板为单个模板
    is_i_start = False
    is_n_start = False
    is_question_start = False
    sql_template_back = ''
    for item in sql_template:
        if item.lower() == 'i':
            is_i_start = True
        else:
            if is_i_start:
                if item.lower() == 'n':
                    is_i_start = False
                    is_n_start = True
                else:
                    is_i_start = False
            else:
                if is_n_start:
                    # 是否应该考虑 hint段? 暂时不考虑
                    if item.isalpha():
                        is_n_start = False
                    elif item == '?':
                        is_n_start = False
                        is_question_start = True
                else:
                    if is_question_start:
                        if item in ['?', ',', ' ']:
                            continue
                        elif item == ")":
                            is_question_start = False
        sql_template_back += item
    sql_template = sql_template_back
    print("sql_template: %s" % sql_template)

    return sql_template
