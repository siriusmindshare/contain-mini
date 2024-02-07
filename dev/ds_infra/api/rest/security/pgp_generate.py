import os
from importlib import import_module
import ds_infra.api.rest.common.constants

import importlib

import importlib
gnupg_spec = importlib.util.find_spec("gnupg")
gnupg_found = gnupg_spec is not None
if gnupg_found :
    import gnupg
import ds_infra.api.rest.common.utils
from ds_infra.api.rest.common.utils import log
import logging
import ds_infra.api.rest.common.constants


def setup():
    os.system('rm -rf ../ds_infra/gpghome')
    os.system('mkdir ../ds_infra/gpghome')

def connect():
    try :
        #gpg = gnupg.GPG(gnupghome='./ds_infra/gpghome/', gpgbinary='/usr/local/gnupg-2.2/bin/gpg')
        #gpg = gnupg.GPG(gnupghome='gpghome/')
        gpg = gnupg.GPG(gnupghome='/ds_infra/ds_infra/gpghome/')
        return gpg
    except Exception as e :
        log("could not connect to pgp",level=logging.INFO)
        raise e

def generate_keys():

    if gnupg_found and not ds_infra.api.rest.common.constants.__HTTPS__:
        setup()

        gpg = connect()

        #input_data = gpg.gen_key_input(
        #    name_email='venkata@siriusmindshare.com',
        #   passphrase='omc_pyservice')

        input_data = gpg.gen_key_input(
            name_email='venkata@siriusmindshare.com',
           passphrase='oracle')

        key = gpg.gen_key(input_data)
        log(key,level=logging.INFO)


        ascii_armored_public_keys = gpg.export_keys(str(key.fingerprint))
        ascii_armored_private_keys = gpg.export_keys(str(key.fingerprint), secret=True,passphrase='omc_pyservice')
        #with open('./gpghome/omc_key_pyservice.asc', 'w') as f:
        with open('./ds_infra/gpghome/omc.asc', 'w') as f:
        #with open('./gpghome/omc.asc', 'w') as f:
            f.write(ascii_armored_public_keys)
            f.write(ascii_armored_private_keys)


        unencrypted_string = 'test123' #OMC DB PWD
        encrypted_data = gpg.encrypt(unencrypted_string, 'venkata@siriusmindshare.com')
        encrypted_string = str(encrypted_data)
        log ('ok: %s '% encrypted_data.ok,level=logging.INFO)
        log ('status: %s ' % encrypted_data.status,level=logging.INFO)
        log ('stderr: %s ' % encrypted_data.stderr,level=logging.INFO)
        log ('unencrypted_string: %s ' % unencrypted_string,level=logging.DEBUG)
        log ('encrypted_string: %s ' % encrypted_string,level=logging.DEBUG)

def encrypt_keys(unencrypted_string):
    if gnupg_found and not ds_infra.api.rest.common.constants.__HTTPS__:

        gpg = import_keys()

        #unencrypted_string = 'test123'  # OMC DB PWD
        #encrypted_data = gpg.encrypt(unencrypted_string, 'venkata.duvvuri@siriusmindshare.com')
        encrypted_data = gpg.encrypt(unencrypted_string ,'73C9D75BF01DC23BD7A4E5FD8E786D73E91B80F8')
        encrypted_string = str(encrypted_data)

        log ('ok: %s ' % encrypted_data.ok,level=logging.INFO)
        log ('status: %s ' % encrypted_data.status,level=logging.INFO)
        log ('stderr: %s ' % encrypted_data.stderr,level=logging.INFO)
        log ('unencrypted_string: %s'% unencrypted_string,level=logging.DEBUG)
        log ('request encrypted_string: %s' % encrypted_string,level=logging.DEBUG)
        #log("original_encrytion %s" % str(gpg.encrypt("oracle", '73C9D75BF01DC23BD7A4E5FD8E786D73E91B80F8')))
        #log("original_encrytion repr %s " % repr(str(gpg.encrypt("oracle", '73C9D75BF01DC23BD7A4E5FD8E786D73E91B80F8'))))
        #log ("decryption %s " % decrypt_string(str(gpg.encrypt("oracle", '73C9D75BF01DC23BD7A4E5FD8E786D73E91B80F8'))))

        return encrypted_string
    else:
        return unencrypted_string

def import_keys():
    if gnupg_found and not ds_infra.api.rest.common.constants.__HTTPS__:
        try :

            gpg = connect()
            key_data = open('./ds_infra/gpghome/omc.asc').read()
            import_result = gpg.import_keys(key_data)
            #log("""" imported keys1::""",level=logging.INFO)
            #log(import_result.results,level=logging.INFO)
            #log("""" list keys::""",level=logging.INFO)
            #gpg.list_keys()
            return gpg
        except Exception as e :
            log("could not import keys",level=logging.INFO)
            raise e



def decrypt_string(encrypted_string):
    if gnupg_found and not ds_infra.api.rest.common.constants.__HTTPS__:
        try :
            gpg = connect()
            import_keys()
            #decrypted_db_pwd = gpg.decrypt(encrypted_string, passphrase='omc_pyservice')
            decrypted_db_pwd = gpg.decrypt(encrypted_string, passphrase='oracle')

            #log("decrypted_data DB_passsword: %s " % decrypted_db_pwd,level=logging.DEBUG)
            return str(decrypted_db_pwd)
        except Exception as e :
            log("could not decrypt string",level=logging.INFO)
            raise e
    else:
        return encrypted_string
