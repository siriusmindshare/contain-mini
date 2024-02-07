import abc
import configparser
import pandas as pd
import pickle

import ds_infra.api.rest.logging.logger
import ds_infra.api.rest.common.config
import ds_infra.api.rest.common.request


import ds_infra.api.rest.common.utils

import logging

class AbstractProject(abc.ABC):

    # reads config
    def __init__(self, query, conn, test=False,workflow_name=None):
        self.query = query  # payload


        if workflow_name == None:
            self.request = ds_infra.api.rest.common.request.Request(query, test=test)
        else:
            if workflow_name == "rfm":
                self.request = ds_infra.api.rest.common.request.RFMScoreRequest(query,test=test)
        self.loadedModel = None
        self.config = ds_infra.api.rest.common.config.read_project_config(test)
        self.siteId = self.request.getaccountId()
        self.conn = conn

    @abc.abstractmethod
    def predict(self):
        pass

    @abc.abstractmethod
    def train(self):
        pass


    @abc.abstractmethod
    def preprocess(self):
        pass

    def log(self,msg,level=logging.INFO):
        ds_infra.api.rest.common.utils.log(str(msg),level)

