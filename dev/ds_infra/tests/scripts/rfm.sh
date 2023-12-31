#!/bin/bash
echo "building the model"

#curl  --header "Content-Type: application/json"   --request POST   --data '{"accountId":"123","workflowExecId":"10052","workflowTaskId":"10054","workflowName":"rfm","modelName":"model1","actionType":"predict", "modelInputPayload": "{}", "modelStoredTableName": "{}", "runStatus": "", "modelPredictedTableName":"", "dbUrl":"oracle_db:1521:ORCLPDB1.localdomain","dbUser":"contain","sysAdminDbUrl":"oracle_db:1521:ORCLPDB1.localdomain", "dbPassword":"oracle", "sysAdminDbUser":"contain","sysAdminEncryptedPwd":"oracle","custEncryptedPwd":"oracle", "datasource": "[ {  \"dbUser\": \"contain\", \"dbURL\": \"oracle_db:1521:ORCLPDB1.localdomain\",  \"dbPassword\":\"oracle\",   \"dbName\": \"datawarehouseDB\" },  {  \"dbURL\": \"oracle_db:1521:ORCLPDB1.localdomain\", \"dbUser\": \"contain\", \"dbPassword\": \"oracle\",   \"dbName\": \"custDB\"  } ]"  }' -k https://localhost:5000/api/v1/product1/rfm/predict
curl  --header "Content-Type: application/json"   --request POST   --data '{"accountId":"123","workflowExecId":"10052","workflowTaskId":"10054","workflowName":"rfm","modelName":"model1","actionType":"predict", "modelInputPayload": "{}", "modelStoredTableName": "{}", "runStatus": "", "modelPredictedTableName":"", "dbUrl":"73.222.84.xxx:1522:freepdb1","dbUser":"hr","sysAdminDbUrl":"73.222.84.xxx:1522:freepdb1", "dbPassword":"xxx", "sysAdminDbUser":"hr","sysAdminEncryptedPwd":"xxx","custEncryptedPwd":"oracle", "datasource": "[ {  \"dbUser\": \"hr\", \"dbURL\": \"73.222.84.xxx:1522:freepdb1\",  \"dbPassword\":\"oracle\",   \"dbName\": \"datawarehouseDB\" },  {  \"dbURL\": \"73.222.84.xxx:1522:freepdb1\", \"dbUser\": \"hr\", \"dbPassword\": \"xxx\",   \"dbName\": \"custDB\"  } ]"  }' -k https://localhost:5000/api/v1/product1/rfm/predict

#echo "response...."


#curl  --header "Content-Type: application/json" --request GET -k https://localhost:5000/api/v1/product1/rfm/get-data?accountId=123
