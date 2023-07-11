# Architecture Visualization Dashboard

The Dashboard uses the data populated by the [Data analysis tool](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/Data_analysis_tool) to generate necessary visualizations in a [Streamlit](https://streamlit.io/) powered dashboard.

The workflow is as below:

<img src= "https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/_img/visualization_dashboard.png" width="900" height="350">

### Pre-requisites before running the app:
1. Populate necessary data using the [Data analysis tool](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/Data_analysis_tool). The relevant information can be found in the corresponding [readme](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Data_analysis_tool/README.md)

    However, if you want to run the Visualization with pre-populated data and without having to run the Data population tool, please run the [smartdelta__pcd_restore_all.sql](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Data_analysis_tool/db_scripts/complete_data_backup/smartdelta__pcd_restore_all.sql) script. This will completely create a pre-populated database called **SmartDelta__PCD** in the mysql db.

2. Configure database settings in the [config.yaml](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Visualization_dashboard/config.yaml) file.


### For deployments *without* docker:
1. Please verify all dependencies are installed using the [requirement.txt](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/Visualization_dashboard/requirements.txt)

2. Run the application as:
	```bash
	  streamlit run streamlit_app.py
	```
 
3. Access the application at:
	```bash
	http://localhost:8501/
	```
 
### To deploy in a container, please follow the following steps:

1. Build a docker image using the Dockerfile:
   ```bash
       docker build -t streamlit .
   ```
	
2. Run the container:
   ```bash
       docker run -p 8501:8501 streamlit
    ```

3. Access the application at:
    ```bash
       http://localhost:8501/
    ```

### To deploy in a container using pre-populated data:

There is also a docker-compose that already deploys the visualization dashboard container along with a mysql db container with per-populated data. Please follow the [readme](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool#running-the-dashboard-with-pre-computed-data) to initiate this setup.

**In this case, the pre-requisites are not necessary**