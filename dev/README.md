

# Data science REST Services

This refers to version 1 of `ds_infra`, i.e., the DS Intelligent REST Services for model fitting and REST API for prediction. It is heavily marketing specific at the moment, but will be more product agnostic in future releases. This guides illustrates how to build and run the project locally. It also provides guidance on how to add features to the package.


# Order of Execution

Below is the order of execution once the app's entry point is called:

1. The `app.py.__main__` is called as the main entry point.

2. Env variables are loaded from `ds_infra/ds_infra.env`

3. App is configured using the `connexion/swagger` interface where the `ds_app.yaml` is read to generate REST endpoints.

5. App is started in `HTTPS` or `HTTP` mode. 

  - If `HTTPS` and local, then app will start in `pem` mode. 
    
6. Listen for requests


# Building and deploying the project

Wheel is used to create a distribution:

`pip install wheel`

The following command will build the project and install any required dependencies as listed in the `setup.py` file:

`python setup.py sdist bdist_wheel`


## Versioning

Versioning is handed automatically by using git tags. This is integrated with the `setuptools_scm` package which is used in `setup.py`.

# Getting Started

In order to use the framework, there are a few files that control the configuration, currently `ini` files as required by the  architecture

## config.ini

This file contains project wide settings, db connection info, port info, and the number of processes specified for doing the work.

## project_config.ini

The individual project configuration, e.g, CLV specific configurations, are located here.

## Environment variable files

There are two files with environment variables.

1. `ds_infra/.env` (for local testing)
2.  `ds_infra/ds_infra/ds_infra.env` (for runtime)

The first environment file `.env` is only used locally (on your laptop) for testing and only accessed by `docker-compose` when building the images during the `docker-compose` preprocessing step. These variables are used to fill in values in each of the `docker-compose-*.yml` files. They are NEVER read by the Python application once the container starts. If you change the values, use `docker-compose config` to see the output of the pre-processed `docker-compose-*.yml` file.

The `.env` file specifies where the models, data and logs reside on the local host and docker containers. For local testing, these can live anywhere. But for consistency across machines, make sure you have these dir's (`datafiles`, `models`, `logs`) at your topic level, that is, beside this `README.md`. You can create them like this:

`mkdir {datafiles,models,logs}`

The second environment file `/ds_infra.env` is used exclusively by the Python application and is read upon application start up by a method in the application. These variables are available as part of the `ds_infra` package when the application is deployed, e.g., to staging or production.

# Docker

This application is meant to be containerized. Therefore all integration testing should be executed from within the running container.

## docker-compose files:

There are several scenarios for using `ds_infra` with docker and corresponding docker-compose files to support them. For most DS developers of specific features, you'll want to use option 3 or 4 below, since you're not actively developing `ds_infra` itself:


1. docker-compose.yml: To only build `ds_infra` image
2. docker-compose-with-db.yml: To build `ds_infra` image and use DB image



These can be run with the `docker-up.sh` script like this:

`./docker-up.sh docker-compose-with-db.yml`



### Local Setup: Building images from scratch, Using docker-compose-with-db.yml

If you do not want to use artifactory and want to build ds_infra image from scratch along with DB image, then you can attempt to test locally by running the ds_infra service and a local db service.
`docker-compose-with-db.yml` contains the configuration to setup a local docker container with Oracle DB in addition to building the ds\_infra container.

1. To use this, follow step 1 from above: pull enterprise:12.2.0.1-slim `docker pull omcds-docker.dockerhub-den.siriuscorp.com/database/enterprise:12.2.0.1-slim` 
2. Once it downloads, run `docker-compose -f docker-compose-with-db.yml up --build`
3. Follow steps 4-5 from above 

### Local Setup: Without DB

Just run `docker-compose up --build`, that will bring up the ds\_infra container. Run commands as described in step 5 above
















