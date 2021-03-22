import logging

from component import mymysql, request_dingding_webhook
from config import app_conf

db_2_owner = {}
owner_2_db = app_conf["owner_2_db"]
for (owner, db_list) in owner_2_db.items():
    for db in db_list:
        if not db_2_owner.__contains__(db):
            db_2_owner[db] = owner
owner_2_phone = app_conf["owner_2_phone"]
owner_2_name = app_conf["owner_2_name"]

logger = logging.getLogger('sync_polardb_slow_log')
logger.setLevel(logging.DEBUG)


def post_alarm(msg_content, at_mobiles):
    dingding_webhook_access_token = app_conf["dingding_webhook_access_token"][0]
    dingding_resp = request_dingding_webhook.request_dingding_webhook(dingding_webhook_access_token, "服务严重慢SQL",
                                                                      msg_content,
                                                                      at_mobiles)
    logger.debug(dingding_resp)


def select_serious_sql(special_day):
    serious_sql_maximum_tolerance_count = app_conf["serious_sql"]["maximum_tolerance_count"]
    grafana_base_url = app_conf["grafana"]["base_url"]
    serious_sql_list = mymysql.execute("""
    SELECT
        t.db_name,
        t.sql_template_id,
        t.sql_count
    FROM
        ( SELECT count( 1 ) AS sql_count, db_name, sql_template_id FROM polardb_slow_log WHERE execution_start_time LIKE %s GROUP BY db_name, sql_template_id ) t 
    WHERE
        t.sql_count >= %s
        order by t.sql_count desc
    """, [special_day, serious_sql_maximum_tolerance_count])
    alarm_title = "%s %s种严重慢SQL(%s次+):\n\n" % (
        special_day[:-1], len(serious_sql_list), serious_sql_maximum_tolerance_count)
    """
    | 数据库名称: SQL模板ID | 慢SQL次数 | 数据库负责人 |
    | --------------------- | --------- | ------------ |
    | wms: 1                | 5         | 喻庆捷       |  
    """
    alarm_msg = "| 数据库名称-SQL模板ID | 慢SQL次数 | 数据库负责人 \n\n"
    alarm_msg += "| --------------------- | --------- | ------------ \n\n"
    at_mobiles = []
    for serious_sql_item in serious_sql_list:
        db_name = serious_sql_item["db_name"]
        sql_template_id = serious_sql_item["sql_template_id"]
        sql_count = serious_sql_item["sql_count"]
        owner_ = db_2_owner[db_name]
        owner_phone = owner_2_phone[owner_]
        if owner_phone not in at_mobiles:
            at_mobiles.append(owner_phone)
        owner_name = "@%s" % owner_phone
        link_grafana_url = grafana_base_url.format(db_name=db_name, sql_template_id=sql_template_id)
        db_name__sql_template_id = "%s-%s" % (db_name, sql_template_id)
        display_db_name__sql_template_id = "[%s](%s)" % (db_name__sql_template_id, link_grafana_url)
        alarm_msg += "| %s                | %s 次        | %s\n\n" % (
            display_db_name__sql_template_id, sql_count, owner_name)
    msg_content = alarm_title + alarm_msg
    post_alarm(msg_content, at_mobiles)
