import pkg_resources
from environs import Env

__DBPWD_ADMIN__ = "default"
__DBPWD_PROJECT__ = "default"

__FLASK_PORT__ = None
__HTTPS__ = None
__PUBLIC_CERT__ = None
__PRIVATE_KEY__ = None
__CONTAINER_HOME_CERT__ = None
__KEYSTORE_DIR__ = None
__KEYALIAS__ = None
__LOGLEVEL__ = None


"""
Called from app.py. Designed like this so env vars are read only once.
"""
def init_env_vars():

    global __FLASK_PORT__
    global __HTTPS__
    global __PUBLIC_CERT__
    global __PRIVATE_KEY__
    global __CONTAINER_HOME_CERT__
    global __KEYSTORE_DIR__
    global __KEYALIAS__
    global __LOGLEVEL__

    env = Env()
    env.read_env(pkg_resources.resource_filename("ds_infra", "ds_infra.env"), recurse=False)

    __FLASK_PORT__ = env.int("REST_PORT")
    __HTTPS__  = env.bool("HTTPS")
    __PUBLIC_CERT__  = env.str("PUBLIC_CERT")
    __PRIVATE_KEY__  = env.str("PRIVATE_KEY")
    __CONTAINER_HOME_CERT__  = env.str("CONTAINER_HOME_CERT")
    __KEYSTORE_DIR__ = env.str("KEYSTORE_DIR")
    __KEYALIAS__ = env.str("KEYALIAS")
    __LOGLEVEL__ = env.int("LOGLEVEL")

# various request/response related strings
SUBMITTED = "SUBMITTED"
OK = "OK"
FAILED = "FAILED"
RUNNING = "RUNNING"
COMPLETED = "COMPLETED"
POLL_FAILED = "POLL_FAILED"
FULL = "FULL"
NA = "NA"


