# How to install Oracle database for database migration

## Run Oracle in docker

    mkdir oracle-data
    docker run -d -p 8085:8080 -p 1521:1521 -v "$(pwd)/oracle-data:/u01/app/oracle" quay.io/maksymbilenko/oracle-12c

## Download the latest database dump

It can be found from the Hitas remote desktop machine or ask around for it :)

## Load the dump

    cp <hitas.dmp> oracle-data/admin/xe/dpdump/EXPDAT01.DMP

## Install Oracle SQL Developer

Download it [here](https://www.oracle.com/database/sqldeveloper/).

## Add database into Oracle SQL Developer

Press `Create a Connection Manually`
Fill the following information:

```
Name: Oracle
Username: system
Password: oracle
```

Press `Connect`.

## Run the following SQL command

    alter system set DB_CREATE_FILE_DEST='/u01/app/oracle/oradata/xe';

## Start Data Pump Import Wizard

1. Open DBA view
   1. `View` -> `DBA`
2. Select `Data Pump` from DBA view
3. Right click on `Data Pump` and select `Data Pump Import Wizard`
4. Set `Type of import` to `Full`
5. Click `Next` four times and then `Finish`.

Import will not successfully finish. That's fine for now.

## Open SQL query editor 

```
alter table HIDAS.HITASLUOVHINTAIND modify C_OMNIMI2 VARCHAR2(120 Byte);
alter table HIDAS.HITEHIND modify C_OMNIMI1 VARCHAR2(120 Byte);
alter table HIDAS.HITEHIND modify C_OMNIMI2 VARCHAR2(120 Byte);
alter table HIDAS.HITHLIHU modify C_HUOPAR VARCHAR2(120 Byte);
alter table HIDAS.HITHUONE modify C_OMNIMI2 VARCHAR2(120 Byte);
alter table HIDAS.HITHUONE modify C_SOTU1 VARCHAR2(120 Byte);
alter table HIDAS.HITHUONEOMISTAJUUS modify C_OMNIMI VARCHAR2(120 Byte);
alter table HIDAS.HITHUONEOMISTAJUUS modify C_OMNIMIUPPER VARCHAR2(120 Byte);
alter table HIDAS.HITHUONEOMISTAJUUS modify C_SOTU VARCHAR2(120 Byte);
alter table HIDAS.HITISAKIRJE modify C_TEKSTI VARCHAR2(120 Byte);
alter table HIDAS.HITLISAT modify TEKSTI1 VARCHAR2(120 Byte);
alter table HIDAS.HITLISAT modify TEKSTI2 VARCHAR2(120 Byte);
alter table HIDAS.HITLISAT modify TEKSTI3 VARCHAR2(120 Byte);
alter table HIDAS.HITLISAT modify TEKSTI4 VARCHAR2(120 Byte);
alter table HIDAS.HITLISAT modify TEKSTI5 VARCHAR2(120 Byte);
alter table HIDAS.HITMARKHINTAIND modify C_OMNIMI2 VARCHAR2(120 Byte);
alter table HIDAS.HITMHIHU modify C_HUOPAR VARCHAR2(120 Byte);
alter table HIDAS.HITMHIND modify C_OMNIMI1 VARCHAR2(120 Byte);
alter table HIDAS.HITMHIND modify C_OMNIMI2 VARCHAR2(120 Byte);
alter table HIDAS.HITMHIYH modify C_YHTPAR VARCHAR2(120 Byte);
alter table HIDAS.HITRAKIHU modify C_HUOPAR VARCHAR2(120 Byte);
alter table HIDAS.HITRAKIND modify C_OMNIMI2 VARCHAR2(120 Byte);
alter table HIDAS.HITRAKIYH modify C_YHTPAR VARCHAR2(120 Byte);
alter table HIDAS.HITVALVO modify C_OSTAJA1 VARCHAR2(120 Byte);
alter table HIDAS.HITVALVO modify C_OSTAJA2 VARCHAR2(120 Byte);
alter table HIDAS.HITVALVO_20061502 modify C_OSTAJA2 VARCHAR2(120 Byte);
alter table HIDAS.HITVALVOOSTAJA modify C_NIMI VARCHAR2(120 Byte);
alter table HIDAS.OKOODI modify C_LYHENNE VARCHAR2(120 Byte);
alter table HIDAS.OKOODI modify C_NIMI VARCHAR2(120 Byte);
alter table HIDAS.OKOODI modify C_SELITE VARCHAR2(120 Byte);
alter table HIDAS.OKOODISTO modify C_LYHENNE VARCHAR2(120 Byte);
alter table HIDAS.OKOODISTO modify C_NIMI VARCHAR2(120 Byte);
alter table HIDAS.OKOODISTO modify C_SELITE VARCHAR2(120 Byte);
```

## Go back to Data Pump Import Wizard

1. Set `Type of import` to `Tables`
2. Click `Next`
3. Select all tables
4. Click `Next` twice
5. Select `Action On Table if Table Exists` and select `Truncate`
6. Click `Next` twice
7. Click `Finish`

## Read import logs

Log files are available in `oracle-data/admin/xe/dpdump/IMPORT-<datestamp>.LOG`

## Check database

1. Select `Oracle Connections` from left menu
2. Select the dataase you created (`Oracle` )
3. Expand `Other Users` 
4. Expand `HIDAS`