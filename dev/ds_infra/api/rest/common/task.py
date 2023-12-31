
import ds_infra.api.rest.common.db


import os
import ds_infra.api.rest.common.request
import ds_infra.api.rest.common.utils
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import ds_infra.api.rest.common.constants
import logging

import socket
import requests
import json


def query_task_server(query):
    req = ds_infra.api.rest.common.request.Request(query)

    sql_statement = """select nvl(python_server_name,'NA') from ML_PROCESSING_STATUS
                       where account_id = %s
                       and workflow_name ='%s'
                       and workflow_task_id  = %s 
                       and workflow_execution_id = %s """ % (req.getaccountId(), req.getworkflowName(),req.gettaskInstanceId(),req.getworkflowExecId() )

    server = str(ds_infra.api.rest.common.db.execute_text_query(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser()))
    log("server is : %s" % server,level=logging.INFO)
    return server


def query_task_pid(query):
    req = ds_infra.api.rest.common.request.Request(query)

    sql_statement = """select nvl(python_pid,-1) from ML_PROCESSING_STATUS
                       where account_id = %s
                       and workflow_name ='%s'
                       and workflow_task_id  = %s 
                       and workflow_execution_id = %s """ % (req.getaccountId(), req.getworkflowName(),req.gettaskInstanceId() ,req.getworkflowExecId() )

    pid = int(ds_infra.api.rest.common.db.execute_number_query(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser()))
    log("pid is : %s" % pid,level=logging.INFO)
    return pid



def get_task_status(query):
    req = ds_infra.api.rest.common.request.Request(query)

    sql_statement = """select run_status from ML_PROCESSING_STATUS
                           where account_id = %s
                           and workflow_name ='%s'
                           and workflow_task_id  = %s  
                           and workflow_execution_id = %s """ % (req.getaccountId(), req.getworkflowName(),req.gettaskInstanceId() ,req.getworkflowExecId() )

    status = ds_infra.api.rest.common.db.execute_text_query(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser())

    if status == "":
       status = ds_infra.api.rest.common.constants.NA

    log("status is : %s" % status,level=logging.INFO)
    return status


def process_exists(pid,query):

    def ping_process():
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True




    log("request host whoami %s" % ds_infra.api.rest.common.utils.flask_host_ip_address(),level=logging.INFO)

    socket_gethostname_port = ds_infra.api.rest.common.utils.flask_host_ip_address()

    task_server_port = query_task_server(query)

    log("request host : %s" % socket_gethostname_port,level=logging.INFO)



    if task_server_port == socket_gethostname_port:
        return ping_process()
    else:
        # redirect request to right sever

        query_poll = query.copy()
        query_poll['pythonServerName'] = task_server_port
        log("sending redirect json query %s" % query_poll,level=logging.INFO)
        log("task_server %s " %task_server_port,level=logging.INFO)
        try :
            if ds_infra.api.rest.common.constants.__HTTPS__:
                #response = requests.post('https://'+ task_server_port+ '/ds/internal/poll', json=query_poll,verify=ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__+ '/' + ds_infra.api.rest.common.constants.__PRIVATE_KEY__)
                response = requests.post('https://' + task_server_port + '/ds/internal/poll', json=query_poll,
                                         verify=False)
            else:
                response = requests.post('http://' + task_server_port + '/ds/internal/poll', json=query_poll)
            log("%s %s %s " % (response.text,response.status_code, response.reason) ,level=logging.INFO)
            res = json.loads(response.text)
            if (res["result"] == ds_infra.api.rest.common.constants.FAILED or
            res["result"] == ds_infra.api.rest.common.constants.FULL or
            res["result"] == ds_infra.api.rest.common.constants.POLL_FAILED) :
                return False
            else:
                return True
        except Exception as e:
            log("Could not redirect poll %s " % e,level=logging.INFO)
            return False





