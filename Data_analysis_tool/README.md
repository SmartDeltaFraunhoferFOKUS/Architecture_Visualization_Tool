# Data analysis tool

*The repo contains the initial version of the Architectural data analysis tool.*

The application takes a folder consisting of log files as input and for each file, computes necessary visualization data and populates it in a mysql backend. 

The workflow is as shown in the figure below:

<img src= "https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/_img/diagram_analysis.png" width="750" height="400">

Please follow the following steps to setup and get the app running:

1. Setup the database:
   setup the required database and tables by running the [CREATE_schema_tables.sql](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Data_analysis_tool/db_scripts/CREATE_schema_tables.sql) script in the *./Data_analysis_tool/db_scripts*

2. Configure the application to use the database through the [config.yaml](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Data_analysis_tool/config/dash_config.yaml) file.
	In this file, please provide the details like database host, port, database name, username, and password
	
3. Use the [requirements.txt](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Data_analysis_tool/requirements.txt) file to install all dependencies.

3. Run the app as:
    ```bash
    python main.py -i "<folder_location>"
    ```
The *folder_location* in step 3 should point to a folder that contains the log files which will be scanned to generate diagrams. Sample data is provided within the [/dualstacklogs](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/Data_analysis_tool/dualstackLogs) folder. The folder constitutes of logs from multiple runs of a simple calculator and a Knuth Elevator simulation

**Note: Step 1 should be only run for first-time setup, for subsequent runs, skip this step since database is already created.**
