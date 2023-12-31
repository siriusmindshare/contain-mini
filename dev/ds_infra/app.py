from connexion.resolver import RestyResolver
import connexion
import ds_infra.api.rest.common.utils
import importlib
openssl_spec = importlib.util.find_spec("OpenSSL")
openssl_found = openssl_spec is not None
from ds_infra.api.rest.common import constants
import ds_infra.api.rest.security.p12topem
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import logging
from pkg_resources import get_distribution, DistributionNotFound
from flask_cors import CORS
import os

if __name__ == '__main__':


    # read the ds_infra.env file ONCE and populate env values in
    #    ds_infra.api.rest.common.constants.py
    constants.init_env_vars()

    # Show logs in once place for ALL env var's
    log("__FLASK_PORT__ set to: " + str(constants.__FLASK_PORT__), level=logging.INFO)
    log("__HTTPS__ set to: " + str(constants.__HTTPS__), level=logging.INFO)
    log("__PUBLIC_CERT__ set to: " + constants.__PUBLIC_CERT__, level=logging.INFO)
    log("__PRIVATE_KEY__ set to: " + constants.__PRIVATE_KEY__, level=logging.INFO)
    log("__CONTAINER_HOME_CERT__ set to: " + constants.__CONTAINER_HOME_CERT__, level=logging.INFO)
    log("__KEYSTORE_DIR__ set to: " + constants.__KEYSTORE_DIR__, level=logging.INFO)
    log("__KEYALIAS__ set to: " + constants.__KEYALIAS__, level=logging.INFO)
    log("__LOGLEVEL__ set to: " + str(constants.__LOGLEVEL__), level=logging.INFO)

    try:
        __version__ = get_distribution('ds_infra').version
        log('Starting with ds_infra version: %s ' % __version__, logging.INFO)
    except DistributionNotFound:
        pass

    app = connexion.App(__name__, port=ds_infra.api.rest.common.constants.__FLASK_PORT__, specification_dir='./swagger/',
                   options={"swagger_ui" : True})
    CORS(app.app)

    app.add_api('ds_app.yaml', resolver=RestyResolver('ds_infra.api'))


    # ds_infra.api.rest.common.utils.setUpKeystore()

    if ds_infra.api.rest.common.constants.__HTTPS__:
        # if openssl_found:
        #     pkcs12 = ds_infra.api.rest.security.p12topem.PKCS12Manager(ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__ + '/server.p12', 'root')
        #     log("Starting in https .p12 mode",level=logging.INFO)
        #     app.run(ssl_context=(pkcs12.getCert(), pkcs12.getKey()), host='0.0.0.0',
        #             port=ds_infra.api.rest.common.constants.__FLASK_PORT__, debug=False)w
        #
        # else:
        abs_cert_path = os.path.abspath('/pem/server.cer.pem')
        abs_key_path = os.path.abspath('/pem/server.key.pem')

        print(abs_cert_path)
        print(abs_key_path)

        app.run(ssl_context=(abs_cert_path, abs_key_path), host='0.0.0.0', port=ds_infra.api.rest.common.constants.__FLASK_PORT__, debug=True)

        log("Starting in https pem mode",level=logging.INFO)
        log("Setting pem files as %s %s " % (ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__+ '/'+ds_infra.api.rest.common.constants.__PUBLIC_CERT__, ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__+ '/' + ds_infra.api.rest.common.constants.__PRIVATE_KEY__),level=logging.INFO)
        # app.run(ssl_context=(ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__+
        #                     '/'+ds_infra.api.rest.common.constants.__PUBLIC_CERT__, ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__+ '/' + ds_infra.api.rest.common.constants.__PRIVATE_KEY__ ),
        #         host='0.0.0.0', port=ds_infra.api.rest.common.constants.__FLASK_PORT__, debug=False)
        print(ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__ + '/' + ds_infra.api.rest.common.constants.__PUBLIC_CERT__)
        print(ds_infra.api.rest.common.constants.__CONTAINER_HOME_CERT__ + '/' + ds_infra.api.rest.common.constants.__PRIVATE_KEY__)

        # app.run(ssl_context=("/pem/server.cer.pem", "/pem/server.key.pem"),
        #         host='0.0.0.0', port=ds_infra.api.rest.common.constants.__FLASK_PORT__, debug=False)
    else:
        log("Starting in http mode",level=logging.INFO)
        app.run( host='0.0.0.0',port=ds_infra.api.rest.common.constants.__FLASK_PORT__, debug=True)
