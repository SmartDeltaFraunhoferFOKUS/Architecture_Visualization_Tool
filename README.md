# Architecture visualization Dashboard.

The repo contains two applications:
1. A [Data population tool](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/data_population_tool): computes different views from the given input and stores them in the database. 
2. A [Streamlit dashboard](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/tree/master/streamlit_dashboard): uses the computed data in the database to create a visualization Dashboard.

The general workflow is depicted below:

<img src= "_img/workflow.png" width="900" height="350">


## Running the Dashboard with pre-computed data

To have a quick overview of the Dashboard, we have already created a database with data populated by running the Data population tool on mock datasets (Knuth elevator simulation logs and simple calculator operation logs)

This data can already be used to view sample visualizations via the Dashboard. 

The [dockercompose](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool/blob/master/docker-compose.yaml) file in this directory launches two containers, a mysqldb container with the populated data and the other one, the Streamlit application that attaches to this db.  

For a demo of the Dashboard, just run:

```bash
docker-compose up --build
```

The Dashboard is then exposed in 8501 port. Access the application as:
```bash
http://localhost:8501/
```


