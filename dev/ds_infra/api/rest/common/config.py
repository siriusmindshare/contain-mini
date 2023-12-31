import configparser
import os


def read_main_config(test=False):

    config = configparser.ConfigParser()
    if test:
        config.read('/datascience/tests/test_config.ini')
    else:
        config.read(os.path.join(os.environ['DATASCIENCE_HOME'], "config/config.ini"))

    return config


def read_project_config(test=False):

    config = configparser.ConfigParser()
    if test:
        config.read('/datascience/tests/project_test_config.ini')
    else:
        config.read(os.path.join(os.environ['DATASCIENCE_HOME'], "config/project_config.ini"))

    return config

