import ds_infra.api.rest.common.utils

from ds_infra.api.wrapper.exceptions  import FrameworkException
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import json
import logging

class RfmScoreResponse():
    # reads config
    def __init__(self, response, test=False):

        #log("in request starting ")

        if test:
            log("parsing and loading json as string",level=logging.INFO)
            self.query = json.loads (str(response))  # payload
        else:
            log("parsing and loading json as is",level=logging.INFO)
            self.query = response # TODO
            #self.query = json.loads(str(query))

        try:
            # poll
            self.version = self.query['version']
            self.status = self.query['status']

            self.classification = self.query["data"]["classification"]

            # optional
            try:
                self.subjectline = self.query['data']['subjectline']
                self.launchkey = self.query['data']['externalKey']
                self.modelname = self.query['modelStorage']['model']


            except Exception as e:
                log("optional query parse exception %s " % e, level=logging.INFO)
            log("finished parsing optional poll parameters", level=logging.INFO)

        except KeyError as e:
            log("Malformed Query %s " % e, level=logging.INFO)
            raise FrameworkException("Malformed Response Exception")
        except Exception as e:
            log("Other Input Query Exception %s " % e, level=logging.INFO)
            raise FrameworkException("other Response Exception")

    def getVersion(self):
        return self.version

    def getstatus(self):
        return self.status

    def getprediction(self):
        return self.status


    def getsubjectLine(self):
        return self.subjectline

    def getmodelname(self):
        return self.modelname

    def getExternalKey(self):
        return self.launchkey

    def setstatus(self,status):
        self.status = status


            
