#!/bin/bash

echo "SID_LIST_LISTENER= (SID_LIST= (SID_DESC= (ORACLE_HOME=/u01/app/oracle/product/12.2.0/dbhome_1) (SID_NAME=ORCL)))" >> $TNS_ADMIN/listener.ora
lsnrctl reload

sqlplus / as sysdba << EOF
	ALTER PLUGGABLE DATABASE ORCLPDB1 SAVE STATE;
	ALTER SESSION SET CONTAINER=ORCLPDB1;
    CREATE USER CONTAIN IDENTIFIED BY oracle;
	GRANT CREATE SESSION to CONTAIN;
    GRANT CREATE TABLE TO CONTAIN;
	GRANT UNLIMITED TABLESPACE TO CONTAIN;
	exit;
EOF
echo "Set Password done"

sqlplus contain/oracle@ORCLPDB1<< EOF
	@/scripts/tables
	@/scripts/rows
	@/scripts/rfm_row
	exit;
EOF
echo "Created tables"
