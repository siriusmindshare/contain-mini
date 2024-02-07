import cx_Oracle
import ds_infra.api.rest.common.db
from datetime import datetime
import ds_infra.api.rest.common.request
import ds_infra.api.rest.common.constants
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import logging
from pytz import timezone
import pytz

def update_pid(pid, query):
    req = ds_infra.api.rest.common.request.Request(query)
    now = datetime.now(tz=pytz.utc)
    now = now.astimezone(timezone('US/Pacific'))
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    sql_statement = """UPDATE
    ML_PROCESSING_STATUS
    SET
    run_status = '%s', python_pid = %s ,modified_dt = TO_DATE('%s', 'mm/dd/yyyy hh24:mi:ss')
    WHERE
    account_id = %s and workflow_task_id= %s and workflow_execution_id = %s""" % (
        'RUNNING', pid, date_time ,req.getaccountId(), req.gettaskInstanceId(),req.getworkflowExecId())

    ds_infra.api.rest.common.db.execute_dml(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser())

    return True


def update_status(pid, query, status):
    req = ds_infra.api.rest.common.request.Request(query)
    now = datetime.now(tz=pytz.utc)
    now = now.astimezone(timezone('US/Pacific'))
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    sql_statement = """UPDATE
        ML_PROCESSING_STATUS
        SET
        run_status = '%s',modified_dt = TO_DATE('%s', 'mm/dd/yyyy hh24:mi:ss')
        WHERE
        account_id = %s and workflow_task_id = %s and python_pid = %s and workflow_execution_id = %s""" % (
        status, date_time,req.getaccountId(), req.gettaskInstanceId(), pid,req.getworkflowExecId())

    ds_infra.api.rest.common.db.execute_dml(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser())

    return True


def create_task(query):
    req = ds_infra.api.rest.common.request.Request(query)
    now = datetime.now(tz=pytz.utc)
    now = now.astimezone(timezone('US/Pacific'))
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    log("date and time: %s" % date_time)

    log("query %s " % query)


    sql_statement = """
                insert into ML_PROCESSING_STATUS values (
        %s , --workflow_execution_id NUMBER(38,0) NOT NULL,
        %s , -- workflow_task_id NUMBER(38,0) NOT NULL,
        %s, --task_instance_id NUMBER(38,0) NOT NULL,
        '%s' , --workflow_name VARCHAR2(255 BYTE) NOT NULL,
         %s, --python_pid NUMBER(38,0),
        '%s' ,--model_name VARCHAR2(100 BYTE) NOT NULL,
        '%s', --action_type VARCHAR2(100 BYTE) NOT NULL,
        '%s' , --model_input_payload VARCHAR2(4000 BYTE) NOT NULL,
        '%s' , --model_stored_table_name VARCHAR2(100 BYTE),
        '%s', --model_predicted_table_name VARCHAR2(100 BYTE),
        '%s', --python_server_name VARCHAR2(255 BYTE),
        '%s', --run_status VARCHAR2(50 BYTE),
        '%s', --db_url VARCHAR2(255 CHAR),
        '%s', --db_user VARCHAR2(255 CHAR),
        '%s', --sysadmin_db_url VARCHAR2(255 CHAR),
        '%s', --sysadmin_db_user VARCHAR2(255 CHAR),
        TO_DATE('%s', 'mm/dd/yyyy hh24:mi:ss'), --created_dt TIMESTAMP(6),
        TO_DATE('%s', 'mm/dd/yyyy hh24:mi:ss')  --modified_dt TIMESTAMP(6),
        ) """ % (req.getaccountId(), req.getworkflowExecId(), req.gettaskInstanceId(),  req.getworkflowName(),-1,req.getmodelName(), req.getactionType(),req.getmodelInputPayload(),
                 req.getmodelStoredTableName(),req.getmodelPredictedTableName(),req.getserverName (), ds_infra.api.rest.common.constants.SUBMITTED,
                 req.getdbUrl(),req.getdbUser(),req.getsysAdminDbUrl(),req.getsysAdminDbUser(),date_time, date_time)

    log("statement %s" % sql_statement)

    try:

       ds_infra.api.rest.common.db.execute_dml(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser())
    except Exception as e:
        log("Insert error, some issue with task or workflow id inputs etc. %s " % e)
        raise e


    return True


def select_running_jobs(query):
    req = ds_infra.api.rest.common.request.Request(query)
    log ("about to select running jobs")
    #log("sys admin pwd %s %s %s %s %s %s" % (req.getdb_host(),req.getdb_port(),req.getdb_service(),
    #                                         req.getsys_host(),req.getsys_port(),req.getsys_service()) level=logging.DEBUG)
    sql_statement = """select nvl(count(*),0) from ML_PROCESSING_STATUS
                       where workflow_name ='%s'
                       and run_status = '%s' """ % (req.getworkflowName(), ds_infra.api.rest.common.constants.RUNNING)
    log ("executing %s " % sql_statement )
    #log("sys admin pwd %s %s %s %s %s %s " % (req.getsysAdminEncryptedPwd(),req.getcustEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser()),level=logging.DEBUG)

    num = int(ds_infra.api.rest.common.db.execute_number_query(sql_statement,req.getsysAdminEncryptedPwd(),req.getsys_host(),req.getsys_port(),req.getsys_service(),req.getsysAdminDbUser()))
    log("running jobs: %s" % num)
    return num
