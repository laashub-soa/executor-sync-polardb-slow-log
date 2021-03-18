import json
import logging
import time
from datetime import timedelta, datetime

from aliyunsdkcore.client import AcsClient
from aliyunsdkpolardb.request.v20170801.DescribeSlowLogRecordsRequest import DescribeSlowLogRecordsRequest

from component import mymysql
from config import app_conf

region = app_conf["region"]
client = AcsClient(app_conf["access_key_id"], app_conf["access_secret"], region)

db_cluster_id = app_conf["db_cluster_id"]
logger = logging.getLogger('sync_polardb_slow_log')
logger.setLevel(logging.DEBUG)


def request_slow_log(db_cluster_id, start_datetime, end_datetime, page_number, page_size):
    """
    请求慢SQL日志
    :param db_cluster_id:
    :param start_datetime:
    :param end_datetime:
    :param page_number:
    :param page_size:
    :return:
    """
    request = DescribeSlowLogRecordsRequest()
    request.set_accept_format('json')

    request.set_DBClusterId(db_cluster_id)
    # 格式化前一天的日期
    request.set_StartTime(start_datetime)
    request.set_EndTime(end_datetime)
    request.set_PageNumber(page_number)
    request.set_PageSize(page_size)

    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')
    resp_result = json.loads(response)
    return resp_result


local_cache_sql_template_id_2_text = {}


def select_sql_template_id_by_text(db_cluster_id, db_name, db_node_id, sql_template_text):
    # 在本地查询
    global local_cache_sql_template_id_2_text
    if local_cache_sql_template_id_2_text.__contains__(db_name):
        local_cache_sql_template_id_2_text_db_level = local_cache_sql_template_id_2_text[db_name]
        if local_cache_sql_template_id_2_text_db_level.__contains__(sql_template_text):
            return local_cache_sql_template_id_2_text_db_level[sql_template_text]
    # 在数据库中查询
    sql_template_id = mymysql.execute("""
    SELECT ID FROM polardb_slow_log_template WHERE db_name=%s and convert(sql_text using utf8) = %s
    """, [db_name, sql_template_text])
    sql_template_id = list(sql_template_id)
    if len(sql_template_id) < 1:
        insert_sql_result = mymysql.execute("""
        INSERT INTO `polardb_slow_log_template`(`db_cluster_id`, `db_name`, `db_node_id`, `sql_text`) 
        VALUES (%s, %s, %s, %s)
            """, [[db_cluster_id, db_name, db_node_id, sql_template_text]])
        logger.debug("insert_sql_result: %s" % insert_sql_result)
        sql_template_id = insert_sql_result[0]
    else:
        sql_template_id = sql_template_id[0]["ID"]
    # 更新本地缓存
    logger.debug("sql_template_id: %s" % sql_template_id)
    if not local_cache_sql_template_id_2_text.__contains__(db_name):
        local_cache_sql_template_id_2_text[db_name] = {}
    local_cache_sql_template_id_2_text[db_name][sql_template_text] = sql_template_id
    return sql_template_id


def store_response_result(resp_result):
    """
    存储响应结果
    :param resp_result:
    :return:
    """
    logger.debug("store_response_result")
    # 解析数据
    db_cluster_id = resp_result["DBClusterId"]
    sql_slow_record = resp_result["Items"]["SQLSlowRecord"]
    # 存储数据
    parameters = []
    for item in sql_slow_record:
        # {'QueryTimes': 1, 'ExecutionStartTime': '2021-01-05T00:03:01Z', 'ReturnRowCounts': 0,
        # 'LockTimes': 0, 'DBName': 'wms_7', 'ParseRowCounts': 552904,
        # 'DBNodeId': 'pi-wz973o0ri94iwv5x4', 'HostAddress': 'online_wjhmadb_w[online_wjhmadb_w] @  [192.168.3.10]'
        # , 'SQLText': 'U
        # PDATE `wms_stock` stock SET stock.lock_qty = 0, stock.u_t = unix_timestamp(now()) * 1000 WHERE sto
        # ck.warehouse_id = 7200 AND stock.lock_qty > 0'}
        # 过滤掉一些不用的
        db_name = item["DBName"]
        if db_name == "":  # 数据库名称为空时
            continue
        sql_text = item["SQLText"]
        sql_text_check = sql_text.lower()
        if "binlog dump" in sql_text_check \
                or "dms-data_correct" in sql_text_check \
                or "/*dbs_urv7bfsmb4mx*/%" in sql_text_check \
                or "select @@session.transaction_read_only" in sql_text_check \
                or "prepare" in sql_text_check \
                or "sleep(" in sql_text_check:  # 其他系统的SQL语句
            continue
        host_address = item["HostAddress"]
        if "online_wjhmadb_r" in host_address or "dms[dms]" in host_address:
            continue
        query_times = item["QueryTimes"]
        if query_times < 2:
            continue
        execution_start_time = item["ExecutionStartTime"]
        # 2021-01-05T00:03:01Z
        data_timestamp = int(
            time.mktime(time.strptime(execution_start_time[:-6] + "00:00Z", '%Y-%m-%dT%H:%M:%SZ')))  # 丢失掉秒钟精度
        db_node_id = item["DBNodeId"]
        # 生成sql模板
        sql_template_text = mymysql.extra_sql_template(sql_text)
        sql_template_id = select_sql_template_id_by_text(db_cluster_id, db_name, db_node_id, sql_template_text)
        parameters.append([
            db_cluster_id, db_name,
            item["DBNodeId"], execution_start_time, host_address,
            item["LockTimes"], query_times, item["ParseRowCounts"],
            item["ReturnRowCounts"], sql_text, data_timestamp,
            sql_template_id
        ])
    if len(parameters) < 1:
        return
    mymysql.execute("""
    INSERT INTO `polardb_slow_log`(`db_cluster_id`, `db_name`
    , `db_node_id`, `execution_start_time`, `host_address`
    , `lock_times`, `query_times`, `parse_row_counts`
    , `return_row_counts`, `sql_text`, `data_timestamp`
    , `sql_template_id`
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, parameters)


def clear_day_data(day_interval):
    """
    清理某一天数据
    :param day_interval: 时间间隔
    :return:
    """
    day_name = (datetime.today() + timedelta(day_interval)).strftime("%Y-%m-%d") + "%"
    mymysql.execute("""
    delete 
    from polardb_slow_log
    where execution_start_time like %s
    """, [day_name])


def service(day_interval):
    start_datetime = (datetime.today() + timedelta(day_interval)).strftime("%Y-%m-%d") + "T00:00Z"
    end_datetime = (datetime.today() + timedelta(day_interval + 1)).strftime("%Y-%m-%d") + "T00:00Z"
    logger.debug("start_datetime - end_datetime: %s - %s" % (start_datetime, end_datetime))
    page_number = 1
    page_size = 100
    max_page_number = 0
    fail_try_again_count = 0
    error_try_again_count = 0
    while True:
        resp_result = None
        start_time_second = int(time.time())
        try:
            resp_result = request_slow_log(db_cluster_id, start_datetime, end_datetime, page_number, page_size)
            if max_page_number == 0:
                total_record_count = resp_result["TotalRecordCount"]
                if total_record_count < 1:
                    if error_try_again_count < 100:
                        error_try_again_count += 1
                        logger.debug("error page try again:%s in %s second after" % (
                            error_try_again_count, error_try_again_count))
                        time.sleep(error_try_again_count)
                        continue
                    else:
                        break
                max_page_number = int(total_record_count / page_size) + 1

        except Exception as e:
            logger.debug("发生了异常: " + str(e))
            if fail_try_again_count < 100:
                fail_try_again_count += 1
                logger.debug("fail request try again:%s in %s second after" % (
                    fail_try_again_count, fail_try_again_count))
                time.sleep(fail_try_again_count)
                continue
        finally:
            logger.debug("page_number: %s/%s page_size: %s time_cost: %sS " % (
                page_number, max_page_number + 1, page_size, (int(time.time()) - start_time_second)))
        if resp_result:
            store_response_result(resp_result)
        if page_number > max_page_number:
            break
        else:
            page_number += 1
        fail_try_again_count = 0
        time.sleep(1)


def start():
    global local_cache_sql_template_id_2_text
    local_cache_sql_template_id_2_text = {}
    day_interval = -1
    # while True:
    #     clear_day_data(day_interval)
    #     service(day_interval)
    #     day_interval += -1
    clear_day_data(day_interval)
    service(day_interval)
