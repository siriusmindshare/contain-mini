"""
    API handler
"""

import json

import ds_infra.api.rest.common.db
import ds_infra.api.rest.common.query
import ds_infra.api.rest.common.config
import ds_infra.api.rest.common.constants
from ds_infra.api.wrapper.exceptions  import FrameworkException

import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import logging

"""
    Prediction service
"""
import importlib
import ds_infra.api.rest.common.request
import ds_infra.api.rest.common.response
import time

"""
    Dynamic loading of project
"""

def load_project(query, test=False,workflow_name=None,db=True):


    config = ds_infra.api.rest.common.config.read_project_config()

    if workflow_name == None:
        req = ds_infra.api.rest.common.request.Request(query)
        workflow_name = req.getworkflowName()
    else:     
        if workflow_name == "rfm":
            req = ds_infra.api.rest.common.request.RFMScoreRequest(query)        
    project_class_name = config['model_' + workflow_name]['project_main_class']
    project_folder = config['model_' + workflow_name]['project_folder']
    project = 'ds_infra.Product1.projects.' + str(project_folder) + '.project'
    log('loading project %s' % project,level=logging.INFO)
    module = importlib.import_module(project)
    log('loading project class %s ' % project_class_name,level=logging.INFO)
    project_class = getattr(module, project_class_name)

    #conn = ds_infra.api.rest.common.db.connect(req.admin=False)

    if db:

        if not hasattr(req, 'db_dict'):
            # default cust db connection
            conn = ds_infra.api.rest.common.db.connect(user=req.getdbUser(), host=req.getdb_host(), service=req.getdb_service(), port=req.getdb_port(),db_encrypted_pwd = req.getcustEncryptedPwd(),admin=False,db_dict = None,test=False)
        else:
            # many db connections
            conn= ds_infra.api.rest.common.db.connect(user=None, host=None,
                                                       service=None, port=None,
                                                       db_encrypted_pwd=None, admin=False,db_dict = req.db_dict,
                                                       test=False)
    else:
        conn = None
    project = project_class(query,conn)

    return project,conn


"""
    Predict service
"""

def predict(query,tasks_status_dict,meta_data,pid_keys, test=False):

    workflowName=None
    log(f"in predict --- {query['workflowName']}",level=logging.INFO)

    if "workflowName" in query:
        workflowName = query['workflowName']

    project, conn = load_project(query,test, workflow_name=workflowName)

    try:

        tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.RUNNING
        log('checkpoint 1 complete', level=logging.INFO)

        log(f"Pids Keys: {pid_keys}", level=logging.INFO)

        ds_infra.api.rest.common.query.update_pid(pid_keys[json.dumps(query)],query)
        log('checkpoint 2 complete', level=logging.INFO)
        # Get prediction from model

        #project.preprocess() #TODO

        project.predict() # TODO
        log('checkpoint 3 complete', level=logging.INFO)


    except Exception as e:

        tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED
        ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query, ds_infra.api.rest.common.constants.FAILED)
        ds_infra.api.rest.common.db.disconnect(conn)
        log("job failed %s "% e,level=logging.INFO)
        return False

    #close connection
    ds_infra.api.rest.common.db.disconnect(conn)

    tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.COMPLETED

    ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query, ds_infra.api.rest.common.constants.COMPLETED)


    return True





"""
    Train service
"""
def train(query,tasks_status_dict,meta_data,pid_keys,test=False):
    log("in train",level=logging.INFO)
    project,conn = load_project(query,test)


    try:
        tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.RUNNING

        ds_infra.api.rest.common.query.update_pid(pid_keys[json.dumps(query)],query)

        project.preprocess()

        project.train()


    except Exception as e:
        log("Project class exception %s " %e,level=logging.INFO)
        tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED
        ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query, ds_infra.api.rest.common.constants.FAILED)
        log("job failed",level=logging.INFO)
        ds_infra.api.rest.common.db.disconnect(conn)
        raise FrameworkException ("Project class exception ")
        return False

    ds_infra.api.rest.common.db.disconnect(conn)

    tasks_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.COMPLETED

    ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query, ds_infra.api.rest.common.constants.COMPLETED)

    log("job suceeded",level=logging.INFO)

    return True


"""
    Predict service
"""

def score(query,predictions_status_dict,meta_data,pid_keys, workflow_name, return_dict, test=False):

    log("in score",level=logging.INFO)
    if workflow_name == "xyz":
        # db connection needed
        project,conn = load_project(query,test,workflow_name,db=True)
    else:
        # no db connection needed
        project, conn = load_project(query, test, workflow_name, db=False)

    try:
        predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.RUNNING

        #ds_infra.api.rest.common.query.update_pid(pid_keys[json.dumps(query)],query)
        # Get prediction from model

        #project.preprocess() #TODO

        response = project.predict() # TODO

        log(f"\n\nResponse in main.py (raw) { response }\n\n {dir(response)}\n\n", level=logging.INFO)

        #time.sleep(5)

        try:
            # parse response
            pass
            
        except Exception as e:
            predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED
            #ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query,
            #                                             ds_infra.api.rest.common.constants.FAILED)
            ds_infra.api.rest.common.db.disconnect(conn)
            log("job failed %s " % e, level=logging.INFO)


    except Exception as e:

        predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.FAILED
        #ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query, ds_infra.api.rest.common.constants.FAILED)
        ds_infra.api.rest.common.db.disconnect(conn)
        log("job failed %s "% e,level=logging.INFO)
        return_dict[query] = { "status": "FAILED" }
        return False


    #close connection
    ds_infra.api.rest.common.db.disconnect(conn)

    predictions_status_dict[json.dumps(query)] = ds_infra.api.rest.common.constants.COMPLETED

    #ds_infra.api.rest.common.query.update_status(pid_keys[json.dumps(query)], query, ds_infra.api.rest.common.constants.COMPLETED)


    return True
