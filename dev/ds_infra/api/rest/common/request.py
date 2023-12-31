import ds_infra.api.rest.common.utils

from ds_infra.api.wrapper.exceptions  import FrameworkException
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import json
import logging
import ast
from ast import literal_eval
import requests
import os

def identify_call_type(query):
    if "workflowExecId" in query and query["workflowExecId"] != None:
        if "actionType" in query and query["actionType"] != None:
            # submit call
            return "async-" + str(query["actionType"])
    else:
        return "sync-score"


class Request():
    # reads config
    def __init__(self, query, test=False):

        #log("in request starting ")

        if test:
            log("parsing and loading json as string",level=logging.INFO)
            self.query = json.loads (str(query))  # payload
        else:
            log("parsing and loading json as is",level=logging.INFO)
            self.query = query # TODO
            #self.query = json.loads(str(query))

        try:
            with open('config/ds_infra.env') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    os.environ[key] = value
            user = os.environ.get("USER")
            host = os.environ.get("HOST")
            service = os.environ.get("SERVICE")
            port = os.environ.get("PORT")
            password = os.environ.get("PASSWORD")
            # poll
            self.accountId = self.query['accountId']
            self.workflowExecId = self.query['workflowExecId']
            self.taskInstanceId = self.query['workflowTaskId']
            self.workflowName = self.query['workflowName'].lower()

            self.sysAdminDbUrl = host+":"+str(port)+":"+service
            self.sysAdminDbUser= user
            self.sysAdminEncryptedPwd = password
            self.sys_host= host
            self.sys_port = port
            self.sys_service = service
            log("finished parsing mandatory poll parameters",level=logging.INFO)
            try:
                self.serverName = ds_infra.api.rest.common.utils.flask_host_ip_address()  # query['serverName']
            except Exception as e:
                if test:
                    self.serverName = None
                else:
                    raise e
            log("finished parsing server name %s" % (self.serverName),level=logging.INFO)
            # submit
            try :
                self.modelName = self.query['modelName']
                self.actionType= self.query['actionType']
                self.modelInputPayload= self.query['modelInputPayload']
                self.modelStoredTableName = self.query['modelStoredTableName']
                self.modelPredictedTableName = self.query['modelPredictedTableName']
                try:
                    self.dbUrl= host+":"+str(port)+":"+service
                    self.db_host= host
                    self.db_port = self.dbUrl.split(":")[1]
                    self.db_service = self.dbUrl.split(":")[2]
                    self.dbUser = user
                    self.custEncryptedPwd = password
                except Exception as e:
                    log("db default db parse exception %s " % e, level=logging.INFO)
                self.status= self.query['runStatus']
                # introduced in 20B
                try:
                    datasource = literal_eval(self.query['datasource'])
                    self.db_dict = {}
                    for each_dict in datasource:
                        db = {}
                        db['db_host']= host
                        db['db_port'] = port
                        db['db_service'] = service
                        db['dbUser'] = user
                        db['db_pwd'] = password
                        self.db_dict[str(each_dict['dbName'])] = db
                except Exception as e:
                    log("db datasource dictionary payload parse exception %s " % e, level=logging.INFO)
                    if not 'db' in locals() and not self.custEncryptedPwd in locals():
                        raise FrameworkException("DB Payload Exception. Nor default or datasource dict specified")

            except Exception as e:
                log("optional query parse exception %s " % e,level=logging.INFO)
            log("finished parsing optional poll parameters",level=logging.INFO)

        except KeyError as e :
            log("Malformed Query %s " % e,level=logging.INFO)
            raise FrameworkException("Malformed Exception")
        except Exception as e :
            log("Other Input Query Exception %s " % e,level=logging.INFO)
            raise FrameworkException("other Input Query Exception")


    def getaccountId(self):
        return self.accountId


    def getworkflowExecId(self):
        return self.workflowExecId


    def gettaskInstanceId(self):
        return self.taskInstanceId


    def getworkflowName(self):
        return self.workflowName

    def getmodelName(self):
        return self.modelName

    def getactionType(self):
        return self.actionType

    def getmodelInputPayload(self):
        return self.modelInputPayload

    def getmodelStoredTableName(self):
        return self.modelStoredTableName

    def getmodelPredictedTableName(self):
        return self.modelPredictedTableName

    def getserverName (self):
        return self.serverName

    def getstatus(self):
        return self.status


    def getdbUrl(self):
        if hasattr(self, 'dbUrl'):
            return self.dbUrl
        else:
            return None


    def getdbUser(self):
        if hasattr(self, 'dbUser'):
            return self.dbUser
        else:
            return None

    def getsysAdminDbUrl(self):
        if hasattr(self, 'sysAdminDbUrl'):
            return self.sysAdminDbUrl
        else:
            return None

    def getsysAdminDbUser(self):
        if hasattr(self, 'sysAdminDbUser'):
            return self.sysAdminDbUser
        else:
            return None


    def getsysAdminEncryptedPwd (self):
        if hasattr(self, 'sysAdminEncryptedPwd'):
            return self.sysAdminEncryptedPwd
        else:
            return None



    def getcustEncryptedPwd(self):
        if hasattr(self, 'custEncryptedPwd'):
            return self.custEncryptedPwd
        else:
            return None

    def getdb_host(self):
        if hasattr(self, 'db_host'):
            return self.db_host
        else:
            return None


    def getdb_port(self):
        if hasattr(self, 'db_port'):
            return self.db_port
        else:
            return None


    def getdb_service(self):
        if hasattr(self, 'db_service'):
            return self.db_service
        else:
            return None


    def getsys_host(self):
        if hasattr(self, 'sys_host'):
            return self.sys_host
        else:
            return None


    def getsys_port(self):
        if hasattr(self, 'sys_port'):
            return self.sys_port
        else:
            return None


    def getsys_service(self):
        if hasattr(self, 'sys_service'):
            return self.sys_service
        else:
            return None


class RFMScoreRequest(Request):
    # reads config
    def __init__(self, query, test=False):

        #log("in request starting ")



        if test:
            log("parsing and loading json as string",level=logging.INFO)
            self.query = json.loads (str(query))  # payload
        else:
            log("parsing and loading json as is",level=logging.INFO)
            self.query = query # TODO
            #self.query = json.loads(str(query))
        with open('config/ds_infra.env') as f:
            for line in f:
                key, value = line.strip().split('=')
                os.environ[key] = value
        user = os.environ.get("USER")
        host = os.environ.get("HOST")
        service = os.environ.get("SERVICE")
        port = os.environ.get("PORT")
        password = os.environ.get("PASSWORD")

        try:
            self.actionType= self.query['actionType']
            self.dbUrl= host+":"+str(port)+":"+service
            self.db_host= host
            self.db_port = port
            self.db_service = service
            self.dbUser = user
            self.custEncryptedPwd = password
            self.workflowName = self.query['workflow_name_url']
            self.sysAdminDbUser = user
            self.sysAdminEncryptedPwd = password
            self.sys_host = host
            self.sys_port = port
            self.sys_service = service
        except KeyError as e :
            log("Malformed Query %s " % e,level=logging.INFO)
            raise FrameworkException("Malformed Exception")
        except Exception as e :
            log("Other Input Query Exception %s " % e,level=logging.INFO)
            raise FrameworkException("other Input Query Exception")
    
    def getactionType(self):
        return self.actionType

    def getdbUrl(self):
        if hasattr(self, 'dbUrl'):
            return self.dbUrl
        else:
            return None


    def getdbUser(self):
        if hasattr(self, 'dbUser'):
            return self.dbUser
        else:
            return None

    def getsysAdminDbUrl(self):
        if hasattr(self, 'sysAdminDbUrl'):
            return self.sysAdminDbUrl
        else:
            return None

    def getsysAdminDbUser(self):
        if hasattr(self, 'sysAdminDbUser'):
            return self.sysAdminDbUser
        else:
            return None


    def getsysAdminEncryptedPwd (self):
        if hasattr(self, 'sysAdminEncryptedPwd'):
            return self.sysAdminEncryptedPwd
        else:
            return None



    def getcustEncryptedPwd(self):
        if hasattr(self, 'custEncryptedPwd'):
            return self.custEncryptedPwd
        else:
            return None

    def getdb_host(self):
        if hasattr(self, 'db_host'):
            return self.db_host
        else:
            return None


    def getdb_port(self):
        if hasattr(self, 'db_port'):
            return self.db_port
        else:
            return None


    def getdb_service(self):
        if hasattr(self, 'db_service'):
            return self.db_service
        else:
            return None


    def getsys_host(self):
        if hasattr(self, 'sys_host'):
            return self.sys_host
        else:
            return None


    def getsys_port(self):
        if hasattr(self, 'sys_port'):
            return self.sys_port
        else:
            return None


    def getsys_service(self):
        if hasattr(self, 'sys_service'):
            return self.sys_service
        else:
            return None

    def getworkflowName(self):
        return self.workflowName
