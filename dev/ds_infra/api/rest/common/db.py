import cx_Oracle
import configparser
import ast
import ds_infra.api.rest.security

import ds_infra.api.rest.common.constants
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import logging


def execute_dml(sql_statement,pwd,host,port,service,user):
    log("executing: %s" % sql_statement,level=logging.INFO)

    conn = connect(user=user, host=host, service=service, port=port,db_encrypted_pwd = pwd,admin=True,db_dict = None,test=False)

    if conn is not None:

        log("Connection successful",level=logging.INFO)

        cur = conn.cursor()

        try:
            cur.execute(sql_statement)
        except Exception as e:
            log("Query not successful %s" % str(e),level=logging.INFO)
            conn.commit()
            cur.close()
            return False
        conn.commit()
        cur.close()
        return True
    else:
        log("No Connection",level=logging.INFO)
        return False
    return False


def connect(user=None, host=None, service=None, port=None,db_encrypted_pwd = None,admin=True,db_dict = None,test=False):
    if db_dict == None:
        # default syadmin and database used
        if admin:
            log("Connecting to admin",level=logging.INFO)
            if db_encrypted_pwd is None:
                db_pwd = ds_infra.api.rest.common.constants.__DBPWD_ADMIN__
            else:
                db_pwd = acquire_pwd(db_encrypted_pwd, admin=True)
        else:
            log("Connecting to project",level=logging.INFO)
            if db_encrypted_pwd is None:
                db_pwd = ds_infra.api.rest.common.constants.__DBPWD_PROJECT__
            else:
                db_pwd = acquire_pwd(db_encrypted_pwd, admin=False)

        config = ds_infra.api.rest.common.config.read_main_config()

        if host is None:
            host = str(config['DB']['ip'])
        if service is None:
            service = config['DB']['db']
        if port is None:
            port = config['DB']['port']
        if user is None:
            user = config['DB']['user']

        env = config['ENV']['db']

        if ast.literal_eval(env):

            try:
                #log("Issuing connect to project with %s" %str(user + '/' + db_pwd + '@' + host + ":" + port + "/" +     service),level=logging.DEBUG)
                log("Issuing connect to project with %s" % str(
                    user + '/' + 'HIDDEN' + '@' + host + ":" + port + "/" + service), level=logging.INFO)
                conn = cx_Oracle.connect(user + '/' + db_pwd + '@' + host + ":" + port + "/" + service)
            except Exception as e:

                log("Connection not successful %s" % e,level=logging.INFO)
                raise e
                #return None


            log("Connection successful",level=logging.INFO)

            return conn
        else:
            return None
        return None
    else:
        # 20B
        # need dictionary of DB connections

        log("Connecting to several project dbs", level=logging.INFO)

        conns = {}

        for key,db in db_dict.items():

            user = db['dbUser']
            host = db['db_host']
            service = db['db_service']
            port = db['db_port']
            db_pwd = db['db_pwd']

            try:
                # log("Issuing connect to project with %s" %str(user + '/' + db_pwd + '@' + host + ":" + port + "/" +     service),level=logging.DEBUG)
                log("Issuing connect to project with %s" % str(
                    user + '/' + 'HIDDEN' + '@' + host + ":" + port + "/" + service), level=logging.INFO)
                conn = cx_Oracle.connect(user + '/' + db_pwd + '@' + host + ":" + port + "/" + service)
            except Exception as e:

                log("Connection not successful %s" % e, level=logging.INFO)
                raise e
                # return None

            log("Connection successful to %s " % str(
                    user + '/' + 'HIDDEN' + '@' + host + ":" + port + "/" + service), level=logging.INFO)

            conns[key] = conn
        # return dictionary of connections
        return conns



def disconnect(conn):

    try:
        if conn is not None:
            if type(conn) is not dict:
                conn.close()
            else:
                for name,con in conn.items():
                    con.close()
    except Exception as e:

        log("connection close error %s" % e,level=logging.INFO)


def execute_number_query(sql_statement,pwd,host,port,service,user):
    log("executing: %s" % sql_statement,level=logging.INFO)

    conn = connect(user=user, host=host, service=service, port=port,db_encrypted_pwd = pwd,admin=True,db_dict = None,test=False)

    if conn is not None:

        results = []
        no_jobs = 0

        log("Connection successful",level=logging.INFO)

        cur = conn.cursor()

        try:
            cur.execute(sql_statement)
            for row in cur.fetchall():
                results.append(row)
        except Exception as e:

            log("Query not successful %s " %e,level=logging.INFO)
            conn.commit()
            cur.close()
            return -1


        conn.commit()
        cur.close()

        if len(results) !=0:
            no_jobs = results[0][0]


        log("number = %s " % no_jobs,level=logging.INFO)
        return no_jobs
    else:
        log("No Connection",level=logging.INFO)
        return -1



def execute_text_query(sql_statement,pwd,host,port,service,user):
    log("executing: %s" % sql_statement)

    conn = connect(user=user, host=host, service=service, port=port,db_encrypted_pwd = pwd,admin=True,db_dict = None,test=False)

    if conn is not None:

        results = []
        text = ''

        log("Connection successful")

        cur = conn.cursor()

        try:
            cur.execute(sql_statement)
            for row in cur.fetchall():
                results.append(row)
        except Exception as e:

            log("Query not successful %s" %e)
            conn.commit()
            cur.close()
            return -1


        conn.commit()
        cur.close()

        if len(results) != 0:
            text = results[0][0]


        log("text = %s "% text )
        return text
    else:
        log("No Connection")
        return ''





