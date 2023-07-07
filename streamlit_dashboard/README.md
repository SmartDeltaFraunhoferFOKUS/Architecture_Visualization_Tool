# Architecture Visualization Dashboard

The Dashboard uses the data populated by the [Data population tool](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/data_population_tool) to generate necessary Visualization in a [Streamlit](https://streamlit.io/) powered Dashboard.

Pre-requisites before running the app:
1. Populate necessary data using the [Data population tool](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/data_population_tool)   

However, if you want to run the Visualization with pre-populated data and without having to run the Data population tool, please run the [smartdelta__pcd_restore_all.sql](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/data_population_tool/db_scripts/complete_data_backup/smartdelta__pcd_restore_all.sql) script. This will completely create a pre-populated database called **SmartDelta__PCD** in the mysql db.

2. A running mysql instance with populated data (see step 1).

3. For deployments *without* docker, please verify all dependencies are installed using the [requirement.txt](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/streamlit_dashboard/requirements.txt)

To run the app please follow the following steps:

1. Configure database settings in the [config.yaml](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/streamlit_dashboard/config.yaml) file.

2. Build a docker image using the Dockerfile:
```bash
  docker build -t streamlit .
```
	
4. Run the container:
```bash
docker run -p 8501:8501 streamlit
```

6. Access the application at:
```bash
http://localhost:8501/
```
