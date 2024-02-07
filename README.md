
# Contain-Mini
  
# Deployment

Clone the Repo first to server in `/var/www` location [if other then adjust directories below], create the folder not exist.

## For Backend

Just need to run following command:

`nohup sh ./docker-up.sh docker-compose-with-db.yml &`

  
Note: All the API endpoint should be IP address instead of `localhost/127.0.0.1`

# Testing for local machine for Contain Mini App API

## Prerequisites 
Things you need to install/download
 to start the application


* Docker: 
https://docs.docker.com/get-docker/

* Source code:
download this git repository

There are /dev directories under the folder you just downloaded. 

The /dev contains all the code for the backend service

* Keys:
create ssh keys and store them in dev/ds_infra/pem with following names

dev/ds_infra/pem/server.cer.pem

dev/ds_infra/pem/server.cer.key


## Installation

### Start the backend service:
1. Start docker.
2. Once docker is up and running, go to /dev directory from your terminal, we will name this terminal "docker entry".
3. Create a new folder under /dev with command 'mkdir dist'.
4. Copy the .whl file and .gz file to dist folder you just created.
5. Execute the following code to start the app as a docker container.
```
sh ./docker-up.sh docker-compose-with-db.yml
```
**BE AWARE!**
If you are not building this image for the first time, you may encounter this error:
`
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/user_guide/#fixing-conflicting-dependencies
`
To fix this, go to /dev/dist and delete all the files except the highest version ones (the newest ones created) inside the directory. Then repeat step 5.

6. Wait for the database to setup.
Proceed to step 5 once you see this message.
```
dev-oracle_db-1  | Completed:     alter pluggable database ORCLPDB1 open
dev-oracle_db-1  |     alter pluggable database all save state
dev-oracle_db-1  | Completed:     alter pluggable database all save state
```

7. Initialize database. In another terminal, run
```
docker ps
```
This will show you a table like this:
|   CONTAINER ID   |   IMAGE    | COMMAND | CREATED | STATUS | PORTS | NAMES|
|------------------|------------|---------|---------|--------|-------|------|
| dev-container-id | dev-ds_app |   xxx   | xxxxxxx | xxxxxx | port  |  xx  |
| db-container-id  | database   |   xxx   | xxxxxxx | xxxxxx | port  |  xx  |

Then, run
```
docker exec -it your_db_container_id bash
```

Now we are inside database docker container. Next, run the following command to populate all tables:
```
sh scripts/init-db.sh
```
Grab some snacks, it's gonna take a while.<br />
It might ask you to enter some value. If this happens, just hit enter.

Now we finished initialize the database.

8. Start the app.
open another terminal window and run
```
docker exec -it your_dev_container_id bash
```
then cd to tests/scripts

Next step is to train the model for ad copy app. run
```
sh rfm.sh
```
This step is gonna take a while. Keep an eye on the "docker entry" terminal.<br />
When you see **job suceeded**, it means the training process is finished, you can move to the next step.




 


