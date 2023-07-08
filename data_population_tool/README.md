# Architecture visualization tool

The repo contains the initial version of the Architectural visualization tool.  

The app will compute necessary visualization data and populate it in the mysql backend.

Please follow the following steps to setup and get the app running:

1. Configure the database using the [config.yaml](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/data_population_tool/config/dash_config.yaml) file.

1. *For first time run*, setup the required database and tables by running the [CREATE_schema_tables.sql](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/data_population_tool/db_scripts/CREATE_schema_tables.sql) script in the *./data_population_tool/db_scripts*

2. Run the app as:
```bash
 python main.py -i "<folder_location>"
```

For subsequent runs, skip step 1 since database is already created.
