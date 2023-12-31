
from flask import request
from environs import Env
import ds_infra.api.rest.logging.logger
import logging
from inspect import getframeinfo, stack
import os
import pkg_resources
import logging
from ds_infra.api.rest.common import constants


def flask_host_ip_address():

    return request.host


def debuginfo(message):
    caller = getframeinfo(stack()[2][0])
    return "%s:%d - %s" % (caller.filename, caller.lineno, message)

def log( msg,level=logging.DEBUG):
    #CRITICAL 50
    #ERROR 40
    #WARNING 30
    #INFO 20
    #DEBUG 10
    #NOTSET 0
    logger = ds_infra.api.rest.logging.logger.logger

    if level == logging.DEBUG:
        logger.debug(debuginfo(str(msg)))

    if level == logging.INFO:
        logger.info(debuginfo(str(msg)))

    if level == logging.WARNING:
        logger.warning(debuginfo(str(msg)))



