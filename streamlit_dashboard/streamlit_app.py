__author__ = "Fraunhofer Fokus"
__version__ = "0.1.0"

#import streamlit dependencies
import streamlit as st
import streamlit.components.v1 as components

#import bokeh and related extension for streamlit
from bokeh.plotting import figure, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models import DataTable, TableColumn, HTMLTemplateFormatter,DateFormatter
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

#import streamlit elements
from streamlit_elements import elements, mui, dashboard

#import python libraries
import numpy as np
import pandas as pd
import json
import re
import json
import plotly.express as px
import plotly
import plotly.graph_objs  as go
from datetime import date
import time
#import db related libraries
import mysql.connector
from mysql.connector import Error

#import project internal packages
import db_actions
import settings
import yaml
from datetime import datetime, timedelta

#dashboard config file location
config_file_loc = r"config.yaml"
st.set_page_config(layout="wide")

user ="User1"

d = datetime.today() - timedelta(hours=0, minutes=50)

@st.cache_data
def get_config(config_file_loc):
    """
    Read the database configuration from the config file

    args:
    -------
    config_file_loc: location of the config file

    returns:
    ----------
    a settings.dashboard_configs object that contains dashboard configurations specified in the config yaml file
    """
    with open(config_file_loc, "r") as stream:
        try:
            user_config = settings.user_configs(yaml.safe_load(stream))
            return user_config 
        except yaml.YAMLError as exc:
            print(exc)

@st.cache_resource
def create_cached_connection(_user_config):
    db_obj = db_actions.db_adm(_user_config.dbhost, _user_config.dbusername, _user_config.dbpassword, _user_config.dbname, _user_config.dbport)
    return db_obj

def get_folder_list(db_obj):
    folder_dbquery = "SELECT folderid as fid, foldername, folderlocation FROM tbl_ex_folderinfo"
    records = db_actions.execute_table(db_obj.connection, folder_dbquery)
    return records

def get_file_list(foldername, db_obj):
    filelist_dbquery = "SELECT fi.fileid, filename as FileName, createddate as CreatedDate, modifieddate as ModifiedDate, simfilecount as SimilarityCount, filesize FROM tbl_ex_fileinfo fi, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = '{0}') fo, tbl_viz_qualitymetrics qm  WHERE fi.folderid = fo.folderid and qm.fileid = fi.fileid".format(foldername)
    records = db_actions.execute_table(db_obj.connection, filelist_dbquery)
    return records
    
def draw_fileinfo_grid(pd_dataframe):
    # create plot
    cds = ColumnDataSource(pd_dataframe)
    columns = [    
    TableColumn(field="FileName", title="File Name"),
    TableColumn(field="CreatedDate", title="Created Date", formatter=DateFormatter()),
    TableColumn(field="ModifiedDate", title="Modified Date", formatter=DateFormatter()),
    TableColumn(field="filesize", title="File Size (KB)"),
    TableColumn(field="SimilarityCount", title="Similar Files Count")
    ]

    # define events
    cds.selected.js_on_change(
    "indices",
    CustomJS(
            args=dict(source=cds),
            code="""
            document.dispatchEvent(
            new CustomEvent("INDEX_SELECT", {detail: {data: source.selected.indices}})
            )
            """
        )
    )
    
    p = DataTable(source=cds, columns= columns, css_classes=["my_table"], height=300)
    result = streamlit_bokeh_events(bokeh_plot=p, events="INDEX_SELECT",  key="fileinfo", refresh_on_update=True, debounce_time=0, override_height=300)
 
    if result:
        if result.get("INDEX_SELECT"):
            selected_file=  pd_dataframe.iloc[result.get("INDEX_SELECT")["data"]]["FileName"]            
            return selected_file.iloc[0]
    else:
        return None
    


def draw_sequence_diagram(filename, db_obj):
    dbquery = "SELECT mmd FROM tbl_viz_seqdiagram s, (select fileid FROM tbl_ex_fileinfo f WHERE filename = '{0}') f WHERE f.fileid = s.fileid".format(filename)
    mmd_data = db_actions.execute_table(db_obj.connection, dbquery)

    html_string = """<script src="https://unpkg.com/mermaid@8.0.0/dist/mermaid.min.js"></script><div class="mermaid">{0}</div>""".format(mmd_data["mmd"][0])

    components.html(html_string, width=500, height=520, scrolling=True)    

def plotly_graph(data, axisinfo, _width, _height):
    z_value = data
    x_axis = axisinfo
    y_axis = axisinfo
    text = data
    trace = go.Heatmap(x=x_axis, y=y_axis, z= z_value, text=text, texttemplate= '%{text}',  colorscale = 'Viridis')
    fig = go.Figure(data=trace)
    fig.update_layout(
    autosize=False,
    width=_width,
    height=_height)
    st.plotly_chart(fig, theme="streamlit")

def draw_heatmap(filename, db_obj):
    dbquery = "select data, states from tbl_viz_heatmaps h, (select fileid from tbl_ex_fileinfo f WHERE filename =  '{0}') f WHERE f.fileid = h.fileid".format(filename)
    dataframe = db_actions.execute_table(db_obj.connection, dbquery)

    plotly_graph(json.loads(dataframe["data"][0]), json.loads(dataframe["states"][0]), 850, 500)

def draw_similarity_heatmap(foldername, db_obj):
    dbquery = "SELECT data, axisinfo from tbl_viz_simheatmaps s, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = '{0}') fo WHERE s.folderid = fo.folderid;".format(foldername)
    dataframe = db_actions.execute_table(db_obj.connection, dbquery)

    plotly_graph(json.loads(dataframe["data"][0]), json.loads(dataframe["axisinfo"][0]), 850, 600)

def show_diagrams(selected_file, db_obj):
    sequence_diagram, heatmap = st.columns([0.5,0.5], gap="medium")                    
    with heatmap:
        #draw heatmap
        st.markdown("**State coverage heatmap**")
        draw_heatmap(selected_file, db_obj)
    with sequence_diagram:
        #draw sequence diagram
        st.markdown("**Run-time view**")
        draw_sequence_diagram(selected_file, db_obj)

def draw_dashboard_main(db_obj:db_actions.db_adm):
    #get list of processed folders
    folder_list = get_folder_list(db_obj)    
    #st.image(r"./logo/SmartDelta_logo.png", width=100)
    #define tabs
    dashboard, settings, about = st.tabs([":bar_chart: Dashboard", ":gear: Settings", ":information_source: About"])

    #Dashboard Tab
    with dashboard: 
        #define the dashboard container in the form of an expander (this give a nice boarder)
        with st.expander("", expanded=True):  
            '''### Architecture visualization Dashboard'''
            st.divider()
            #add column to make the selectbox smaller
            selectbox, blank = st.columns([0.3,0.7], gap="large")
            with selectbox:
                selected_folder = st.selectbox("Select a folder to view related dashboard:",options=folder_list["foldername"])

            file_lvl, folder_lvl = st.tabs(["File-level views", "Folder-level views"])            
            with file_lvl:
                #get filelist from the selected folder  
                st.markdown('Showing processed log files within the selected folder, select any file to view related views')
                filelist = get_file_list(selected_folder, db_obj)
                #selected_file = st.selectbox("select a file.", options=filelist)
                selected_file = draw_fileinfo_grid(filelist)
                if (selected_file is not None):
                    show_diagrams(selected_file, db_obj)
            with folder_lvl:
                '''**Heatmaps similarity matrix**'''
                #draw similarity heatmap
                draw_similarity_heatmap(selected_folder, db_obj)
        #st.divider()
        selected_file = None

    #Settings Tab
    with settings:
        dbsettings, User = st.columns([0.5,1], gap="large")
        with dbsettings:               
                        #with st.expander("", expanded=True):
                        st.markdown("#### Database Settings")
                        #with st.expander("Database Settings", expanded=False):
                        st.text_input("Host:", value="Localhost:3306", disabled=True)
                        st.selectbox("Database schema",("smartDelta_PCD",""), disabled=True)
                        st.text_input("Username:", value="root", disabled=True)
                        st.text_input("Password:", value="*******", disabled=True)
                        st.button("Connect", disabled=True)
                        st.divider()
                   
                        #with st.expander("", expanded=True):
                        st.markdown("#### User Settings")     
                        st.write("Currently logged in user: ", user)
                        st.write("logged in since: {0}, {1}".format(date.today(), d.strftime('%H:%M %p')))
                        #st.header("User Settings")       
                        st.button("Logout", disabled=True)
        #st.divider()

    #About Tab
    with about:
        st.markdown('''<font size="2"> <div class="boxed">  Architecture visualization dashboard.  
        Version: 0.1.0  
        Last updated: 06.07.2023 </div> </font>''', unsafe_allow_html=True)

def main():
    user_config = get_config(config_file_loc)
    db_obj = create_cached_connection(user_config)  
    draw_dashboard_main(db_obj)    

if __name__ == '__main__':
    main()