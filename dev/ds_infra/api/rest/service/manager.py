"""
    API handler
"""

import traceback
import sys

import ds_infra.api.rest.security.pgp_generate

import ds_infra.api.wrapper.main
import requests

import json
import ds_infra.api.rest.common.db
import ds_infra.api.rest.common.query
import ds_infra.api.rest.common.task
import ds_infra.api.rest.common.request
import ds_infra.api.rest.common.constants
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log

import ds_infra.api.rest.common.config

from ds_infra.api.wrapper.exceptions  import FrameworkException
import ast

from multiprocessing import Process, Manager

import logging

from flask import request, jsonify

from pkg_resources import get_distribution, DistributionNotFound

# global variables


manager = Manager()
#lock = manager.Lock() # TODO
tasks_status_dict = manager.dict() # TODO
train_processes = []
pid_keys= manager.dict()
predictions_status_dict = manager.dict() # TODO
process_meta_data = manager.dict()
return_dict = manager.dict()


"""
    throttling
"""

def is_task_dict_full(config, query,throttle=True, test = False,req = None):


    if req == None:
        log("default request generation in throttle",level=logging.INFO)
        req = ds_infra.api.rest.common.request.Request(query)

    count = 0
    predictions = 0

    if throttle:

        for key, val in tasks_status_dict.items():
            #log(key,val)
            if val == ds_infra.api.rest.common.constants.RUNNING:
                count += 1

        if ast.literal_eval(config['ENV']['db']):
            try:
                # DB throttle
                #log("running throttling query %s " % (config['THROTTLE']['max_processes_' + req.getworkflowName()]))
                if (int(ds_infra.api.rest.common.query.select_running_jobs(query)) >= int(
                        config['THROTTLE']['max_processes_' + req.getworkflowName()])):

                    return True
                else:
                    return False
            except Exception as e:
                log ("Incorrect project config setup",level=logging.INFO)
                raise FrameworkException("Incorrect config setup")


        else:

            if count >= int(config['THROTTLE']['max_processes_' + req.getworkflowName()]):
                return True
            else:
                return False
    else:

        # prediction service throttling
        log("predictions limiting", level=logging.INFO)

        for key, val in predictions_status_dict.items():
            if val == ds_infra.api.rest.common.constants.RUNNING:
                predictions += 1

        log("predictions count %s " % predictions, level=logging.INFO)
        if predictions >= int(config['LIMIT']['max_score_' + req.getworkflowName()])-1:
            return True
        else:
            return False






"""
    external submit service. 
    asyncronous call
"""

def submit(query):

    try:

        config = ds_infra.api.rest.common.config.read_main_config()
        # identify request type
        query['request_type'] = ds_infra.api.rest.common.request.identify_call_type(query)
        req = ds_infra.api.rest.common.request.Request(query)

        log ("parsed request first time",level=logging.INFO)
        encrypted_string_admin = req.getsysAdminEncryptedPwd()
        #log("encrypted admin pwd : %s" % encrypted_string_admin,level=logging.DEBUG )
        db_pwd_admin = ds_infra.api.rest.common.db.acquire_pwd(encrypted_string_admin,True)

        encrypted_string_project = req.getcustEncryptedPwd()
        #log("encrypted project pwd %s" % encrypted_string_admin ,level=logging.DEBUG)
        db_pwd_project = ds_infra.api.rest.common.db.acquire_pwd(encrypted_string_project,True)

        #log("db pwd %s " % db_pwd_project,level=logging.DEBUG)
        try:
            if is_task_dict_full(config, query,ast.literal_eval(config['ENV']['throttle']) ) != True:


                process_meta_data['db_pwd_project'] = db_pwd_project
                process_meta_data['db_pwd_admin'] = db_pwd_admin

                if (ds_infra.api.rest.common.query.create_task(query)):

                    tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.SUBMITTED

                    if req.getactionType() == 'train':
                        p = Process(target=ds_infra.api.wrapper.main.train, args=(query, tasks_status_dict, process_meta_data,pid_keys))
                        p.start()
                    if req.getactionType() == 'predict':
                        p = Process(target=ds_infra.api.wrapper.main.predict, args=(query, tasks_status_dict, process_meta_data,pid_keys))
                        p.start()

                    # p.join() # dont block
                    pid_keys[json.dumps(query)] = p.pid
                    log ("task %s is done by PROCESS %s " %(json.dumps(query), str(p.pid)),level=logging.INFO)

                    return {
                               "status": ds_infra.api.rest.common.constants.OK,
                                "pythonID":str(pid_keys[json.dumps(query)])

                           }, 200
                else:
                    log("Cannot insert new task in DB",level=logging.INFO)
                    return {
                               "status": ds_infra.api.rest.common.constants.FAILED
                           }, 200
            else:
                return {
                           "status": ds_infra.api.rest.common.constants.FULL
                       }, 200
        except Exception as e:
            log("Unknown exception: %s " % e,level=logging.INFO)
            return {
                       "status": ds_infra.api.rest.common.constants.FAILED
                   }, 200
    except Exception as e:
        return {
                   "status": ds_infra.api.rest.common.constants.FAILED
               }, 400


"""
    external poll service
    synchronous call
    
"""
def poll(query):
    try:

        config = ds_infra.api.rest.common.config.read_main_config()
        query['request_type'] = ds_infra.api.rest.common.request.identify_call_type(query)
        req = ds_infra.api.rest.common.request.Request(query)

        encrypted_string_admin = req.getsysAdminEncryptedPwd()
        #log("encrypted admin pwd %s " % encrypted_string_admin,level=logging.DEBUG)
        db_pwd_admin = ds_infra.api.rest.common.db.acquire_pwd(encrypted_string_admin, True)

        #encrypted_string_project = req.getcustEncryptedPwd()
        #log("encrypted project pwd %s " % encrypted_string_admin)
        #db_pwd_project = ds_infra.api.rest.common.db.acquire_pwd(encrypted_string_project, True)

        #log("db pwd " + db_pwd_project)

        #process_meta_data['db_pwd_project'] = db_pwd_project
        process_meta_data['db_pwd_admin'] = db_pwd_admin

        pid = ds_infra.api.rest.common.task.query_task_pid(query)
        log ("task: %s is done by PROCESS %s " % (json.dumps(query) , str(pid)),level=logging.INFO)
        status = ds_infra.api.rest.common.task.get_task_status(query)
        log ("task: %s status %s " % (json.dumps(query) , str(status)),level=logging.INFO)

        if status == ds_infra.api.rest.common.constants.RUNNING:

            is_alive = ds_infra.api.rest.common.task.process_exists(pid,query)

            log ("task: %s is_alive %s " % (json.dumps(query), str(is_alive)),level=logging.INFO)

            if (is_alive) :
                return {
                         "result": status,
                        }, 200
            else:
                # update failed.
                ds_infra.api.rest.common.query.update_status(pid, query, ds_infra.api.rest.common.constants.FAILED)
                return {
                         "result": ds_infra.api.rest.common.constants.FAILED,
                        }, 200
        else:
            return {
                        "result": str(status)
                    }, 200
    except Exception as e:
        return {
                   "status": ds_infra.api.rest.common.constants.FAILED
               }, 400




"""
Use setuptools_scm for generating a version
"""
def version():

    try:
        __version__ = get_distribution('ds_infra').version
    except DistributionNotFound:
        pass

    return {
        "version": __version__
    }, 200




"""
    external score service
    synchronous call 
"""
def score(query,test=False):
    req = None

    try:

        log("project %s " % request.base_url.split("/")[-2], level=logging.INFO)

        workflow_name_url = request.base_url.split("/")[-2]
        config = ds_infra.api.rest.common.config.read_main_config()
        query['request_type'] = ds_infra.api.rest.common.request.identify_call_type(query)
        query['workflow_name_url'] = workflow_name_url.lower()

        log(f"\n-------------\n\nWorkflow_URL: {workflow_name_url}\n\n", level=logging.INFO)
        
        
        if workflow_name_url == "rfm":
            req = ds_infra.api.rest.common.request.RFMScoreRequest(query)
        try:
            encrypted_string_admin = req.getsysAdminEncryptedPwd()
            #log("encrypted admin pwd : %s" % encrypted_string_admin,level=logging.DEBUG )
            db_pwd_admin = ds_infra.api.rest.common.db.acquire_pwd(encrypted_string_admin,True)

            encrypted_string_project = req.getcustEncryptedPwd()
            #log("encrypted project pwd %s" % encrypted_string_admin ,level=logging.DEBUG)
            db_pwd_project = ds_infra.api.rest.common.db.acquire_pwd(encrypted_string_project,True)

        except Exception as e:
            traceback_str = traceback.format_exc()
            log("DB Service exception: %s " % traceback_str, level=logging.INFO)
            return {
                       "status": ds_infra.api.rest.common.constants.FAILED
                   }, 400

        log("db pwd project %s " % db_pwd_project, level=logging.INFO)
        log("db pwd admin %s " % db_pwd_admin, level=logging.INFO)
        try:
            if is_task_dict_full(config, query,False,test,req) != True:

                if workflow_name_url == "rfm":
                    predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.SUBMITTED
                    p = Process(target=ds_infra.api.wrapper.main.predict, args=(query, predictions_status_dict, process_meta_data,pid_keys))
                    p.start()
                    # pid_keys[json.dumps(query)] = p.pid
                    log ("task %s is done by PROCESS %s " %(json.dumps(query), str(p.pid)),level=logging.INFO)
                
                else:   
                    log(f"Else   \n\n--------------\nWorkflowURL: {workflow_name_url}\n----------------\n",level=logging.INFO)
                    predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.SUBMITTED
                    p = Process(target=ds_infra.api.wrapper.main.score, args=(query, predictions_status_dict, process_meta_data,pid_keys,workflow_name_url,return_dict))
                    p.start()
                    log("prediction %s is done by PROCESS %s " % (json.dumps(query), str(p.pid)), level=logging.INFO)

                if workflow_name_url== "xyz":
                    p.join() # block

                

                pid_keys[json.dumps(query)] = p.pid

                predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.COMPLETED

                
                if workflow_name_url == 'rfm':
                    return {
                        "status": ds_infra.api.rest.common.constants.OK,
                        "pythonID":str(pid_keys[json.dumps(query)])

                    }, 200
                
            
                else:
                    # no proper invocation
                    return {
                            "status": ds_infra.api.rest.common.constants.FAILED
                        }, 400


            else:
                predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED
                return {
                           "status": ds_infra.api.rest.common.constants.FULL
                      }, 400
        except Exception as e:
            predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED

            
            log("Unknown exception: %s \n\n==============\n\n" % e,level=logging.INFO)
            print(traceback.format_exc())


            return {
                       "status": ds_infra.api.rest.common.constants.FAILED
                   }, 400
    except Exception as e:
        predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED
        return {
                   "status": ds_infra.api.rest.common.constants.FAILED
               }, 400




"""
rfm_predict_score for predicting rfm score
"""
def rfm_predict_score(query,test=False):
    return(score(query, test=test))

