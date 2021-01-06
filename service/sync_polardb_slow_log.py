from aliyunsdkcore.client import AcsClient
from aliyunsdkpolardb.request.v20170801.DescribeSlowLogRecordsRequest import DescribeSlowLogRecordsRequest

from config import app_conf

client = AcsClient(app_conf["access_key_id"], app_conf["access_secret"],
                   app_conf["region"])


def request_slow_log():
    request = DescribeSlowLogRecordsRequest()
    request.set_accept_format('json')

    request.set_DBClusterId(app_conf["db_cluster_id"])
    request.set_StartTime("2021-01-05T00:00Z")
    request.set_EndTime("2021-01-06T00:00Z")

    response = client.do_action_with_exception(request)
    print(str(response, encoding='utf-8'))
