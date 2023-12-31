from setuptools import setup, setuptools

import os
os.system('pip install python-dotenv')

from dotenv import load_dotenv
from pathlib import Path
import ast

dotenv_path = Path('./ds_infra/ds_infra.env')
load_dotenv(dotenv_path=dotenv_path)

def import_with_auto_install(package):
    #os.system('pip3 install ' + package)
    import subprocess


setup(
   name='ds_infra',
   version='1.1.1',
   description='data science infrastructure and rest service for contAIn',
   author='Venkata Duvvuri',
   author_email='venkata@siriusmindshare.com',
   include_package_data=True,
   packages=setuptools.find_packages(),
   python_requires='>=3.6',
   use_scm_version = {
        "root": "..",
        "relative_to": __file__,
      #   "local_scheme": "node-and-timestamp"
    },
   setup_requires=['setuptools_scm', 'wheel'],
   install_requires=[
        'Flask==1.1.1',
        'scipy==1.3.1',
        'environs==6.1.0',
        'pandas==0.25.3',
        'numpy==1.17.3',
        'connexion==2.4.0',
        'cx_Oracle==8.3.0',
        'scikit_learn==0.20.1',
        'requests==2.22.0',
        'setuptools_scm==3.4.3',
        'flask-cors==3.0.8',
        'matplotlib==3.3.4',
        'seaborn==0.11.2',
        'yellowbrick',
        'squarify',
        'openpyxl==3.0.4',
        'pulp==2.6.0',
        'sqlalchemy',
        'mlxtend',
        'flask-jwt-extended'
       ],
   entry_points={
    'console_scripts': ['project=ds_infra.app:main'],
   },
)

