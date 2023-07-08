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

#database config file location
config_file_loc = r"config.yaml"

#set page layout to wide so that the dashboard takes the whole screen 
st.set_page_config(layout="wide")

#this is just a placeholder for now to show currently signed-in use in the  "settings" tab
user ="User1"

#This is currently a placeholder to show the time the current user logged in. Currently always 1 hr from current time. But later there are big plans XD
logged_in_since = datetime.today() - timedelta(hours=0, minutes=50)

@st.cache_data
def get_config(config_file_loc:str) -> settings.user_configs:
    """
    Read the database configuration from the config file

    args:
    -------
    * config_file_loc: location of the config file

    returns:
    ----------
    * user_config:  an object that contains dashboard configurations specified in the config yaml file
    """
    with open(config_file_loc, "r") as stream:
        try:
            user_config = settings.user_configs(yaml.safe_load(stream))
            return user_config 
        except yaml.YAMLError as exc:
            print(exc)

@st.cache_resource
def create_cached_connection(_user_config: settings.user_configs) -> db_actions.db_adm:
    """
    Creates an object that contains database connection and other details of the db like username, password, database name and db port

    Args:
    ------------
    * _user_config: user configurations from settings.userconfigs that is used to connect to the db

    Returns:
    ------------
    * db_obj: An object that contains database connection.    
    """
    db_obj = db_actions.db_adm(_user_config.dbhost, _user_config.dbusername, _user_config.dbpassword, _user_config.dbname, _user_config.dbport)
    return db_obj

def get_folder_list(db_obj:db_actions.db_adm) -> pd.DataFrame:
    """
    Queries the database to get list of all current folders, folderids and folder location

    Args:
    --------
    * db_obj: An object that contains database connection.  

    Returns:
    -----------
    * records: a pandas dataframe that contains columns: folderid as fid, foldername, folderlocation FROM tbl_ex_folderinfo
    
    """
    folder_dbquery = "SELECT folderid as fid, foldername, folderlocation FROM tbl_ex_folderinfo"
    records = db_actions.execute_table(db_obj.connection, folder_dbquery)
    return records

def get_file_list(foldername: str, db_obj:db_actions.db_adm) -> pd.DataFrame:
    """
    Queries the database to get list of all files and metadata of files

    Args:
    --------
    * foldername: foldername whose files have to be fetched
    * db_obj: An object that contains database connection.  

    Returns:
    -----------
    * records: a pandas dataframe that contains columns: fileid, FileName, CreatedDate, ModifiedDate, SimilarityCount, and filesize FROM tbl_ex_fileinfo and tbl_viz_qualitymetrics for listing in the grid in the UI    
    """
    filelist_dbquery = "SELECT fi.fileid, filename as FileName, createddate as CreatedDate, modifieddate as ModifiedDate, simfilecount as SimilarityCount, filesize FROM tbl_ex_fileinfo fi, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = '{0}') fo, tbl_viz_qualitymetrics qm  WHERE fi.folderid = fo.folderid and qm.fileid = fi.fileid".format(foldername)
    records = db_actions.execute_table(db_obj.connection, filelist_dbquery)
    return records
    
def draw_fileinfo_grid(pd_dataframe:pd.DataFrame):
    """
    Draws a table that contains details about a file in the dashboard.
    
    Uses bokeh to draw tables. And uses streamlits bokeh events to handle click events to the grid

    Args:
    --------
    * pd_dataframe: A pandas dataframe containing details about a file

    Returns:
    -----------
    * selected_file.iloc[0]: Selected filename when the filelist grid is clicked
    * None: when nothing is selected in the grid 
    """
    cds = ColumnDataSource(pd_dataframe)
    #Define columns for the grid. 
    # Somehow the visibility does not work for now (visible=false property), 
    # if this worked the best thing to do would have been to hide the filied column and the select fileid instead of filename for query,
    # but the bug in Bokeh with visibility hides all the columns if one column is hidden 
    columns = [    
    TableColumn(field="FileName", title="File Name"),
    TableColumn(field="CreatedDate", title="Created Date", formatter=DateFormatter()),
    TableColumn(field="ModifiedDate", title="Modified Date", formatter=DateFormatter()),
    TableColumn(field="filesize", title="File Size (KB)"),
    TableColumn(field="SimilarityCount", title="Similar Files Count")
    ]

    # define events and return a json with data: key
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
    
    #define the bokeh table (height 300 is perfect after a lot of playing around xD)
    p = DataTable(source=cds, columns= columns, css_classes=["my_table"], height=300)
    #use streamlit_bokeh_events to plot table that takes events as well
    result = streamlit_bokeh_events(bokeh_plot=p, events="INDEX_SELECT",  key="fileinfo", refresh_on_update=True, debounce_time=0, override_height=300)
 
    if result:
        if result.get("INDEX_SELECT"):
            selected_file=  pd_dataframe.iloc[result.get("INDEX_SELECT")["data"]]["FileName"]       
            #multiple elements can be selected from the grid and thus "selected_file" itself is a pandas dataframe.
            # the selection thus yields a pandas dataframe like 0 FileName1 1FileName2 (in case of multiple selection), from this selected the first one for now. 
            # select first one by using iloc[0]
            return selected_file.iloc[0]
    else:
        #none return is selectd to prevent error when nothing in the grid is selected. Like when loading the grid for the first time
        return None
    


def draw_sequence_diagram(filename: str, db_obj: db_actions.db_adm):
    """
    Query the database based on the currently selected filename and retrieve the mermaid statements and then plot the sequence diagram
    
    Uses html component of streamlit to draw the sequence diagram

    Args:
    --------
    * filename: filename whose sequence diagram will be drawn
    * db_obj: An object that contains database connection.  
    """
    dbquery = "SELECT mmd FROM tbl_viz_seqdiagram s, (select fileid FROM tbl_ex_fileinfo f WHERE filename = '{0}') f WHERE f.fileid = s.fileid".format(filename)
    mmd_data = db_actions.execute_table(db_obj.connection, dbquery)
    
    #define HTML. The java script and the mermaid class is necessary
    html_string = """<script src="https://unpkg.com/mermaid@8.0.0/dist/mermaid.min.js"></script><div class="mermaid">{0}</div>""".format(mmd_data["mmd"][0])

    components.html(html_string, width=500, height=520, scrolling=True)    

def plotly_graph(data:list, axisinfo:list, _width:int, _height:int):
    """
    Uses the provided data to plot a plotly heatmap
    
    Uses plotly chart component of streamlit to draw the sequence diagram

    Args:
    --------
    * data: a list of arrays that form the actual heatmap
    * axisinfo: a list of strings that form the x and y axis. For instance, for a folder level heatmaps (similarity heatmap), this is the list of foldernames processed. These will be displayed for each cell on the x and y axis  
    * _width: width of the chart
    * _height: height of the chart    
    """  
    z_value = data
    x_axis = axisinfo
    y_axis = axisinfo
    text = data
    #here text=text, texttemplate= '%{text}' puts corresponding numerical values in the heatmap. For instance, for similarity heatmap this is similarity between each component
    trace = go.Heatmap(x=x_axis, y=y_axis, z= z_value, text=text, texttemplate= '%{text}',  colorscale = 'Viridis')
    fig = go.Figure(data=trace)
    fig.update_layout(
    autosize=False,
    width=_width,
    height=_height)
    st.plotly_chart(fig, theme="streamlit")

def draw_heatmap(filename:str, db_obj: db_actions.db_adm):
    """
    Show state transition count inside the selected log file from the folder
    
    Args:
    --------
    * filename: filename hose sequence diagram is to be shown
    * db_obj: An object that contains database connection.
    """  
    dbquery = "select data, states from tbl_viz_heatmaps h, (select fileid from tbl_ex_fileinfo f WHERE filename =  '{0}') f WHERE f.fileid = h.fileid".format(filename)
    dataframe = db_actions.execute_table(db_obj.connection, dbquery)

    #plot the heat map. the width and height are from a lot of trials, but they could def. be better :(
    plotly_graph(json.loads(dataframe["data"][0]), json.loads(dataframe["states"][0]), 850, 500)

def draw_similarity_heatmap(foldername:str, db_obj: db_actions.db_adm):
    """
    Draw pairwise similarity of all the files within the selected folder in a heatmap
    Args:
    --------
    * foldername: selected foldername. Pairwise similarity between all files from the selected folder will be shown
    * db_obj: An object that contains database connection.

    """  
    dbquery = "SELECT data, axisinfo from tbl_viz_simheatmaps s, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = '{0}') fo WHERE s.folderid = fo.folderid;".format(foldername)
    dataframe = db_actions.execute_table(db_obj.connection, dbquery)
    
    #plot the heat map. Again, the width and height are from a lot of trials, but they could def. be better
    plotly_graph(json.loads(dataframe["data"][0]), json.loads(dataframe["axisinfo"][0]), 850, 600)

def show_diagrams(selected_file: str, db_obj: db_actions.db_adm):
    """
    Show the sequence diagram and heatmap of the selected file

    Args:
    --------
    * selected_file: filename of the file whose corresponding diagrams are to be shown
    * db_obj: An object that contains database connection.
    """

    #create two columns, one for showing sequence diagram and another for showing the heatmap
    #the order of the columns defines the order in which columns will be placed in UI from left --> right
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
    """
    Draw components on the dashboard. This will draw tabs, grids, individual architecture diagrams on the UI.

    * db_obj: An object that contains database connection.        
    """

    #get list of processed folders
    folder_list = get_folder_list(db_obj)  
    #Tried placing the logo but the render was so bad. May be with a good resolution image, it gets better   
    #st.image(r"./logo/SmartDelta_logo.png", width=100)

    #define the main tabs
    dashboard, settings, about = st.tabs([":bar_chart: Dashboard", ":gear: Settings", ":information_source: About"])

    #Dashboard Tab
    with dashboard: 
        #define the dashboard container in the form of an expander (this give a nice boarder)
        with st.expander("", expanded=True):  
            '''### Architecture visualization Dashboard'''
            st.divider()
            #add a blank column on the right to make the selectbox for foldername smaller
            selectbox, blank = st.columns([0.3,0.7], gap="large")

            #draw the select box and list the folders within it
            with selectbox:
                selected_folder = st.selectbox("Select a folder to view related dashboard:",options=folder_list["foldername"])

            #Create filelevel and folderlevel tabs.
            # file level tab contains all diagrams that are filelevel
            # folder level tab contains all diagrams that are folderlevel
            file_lvl, folder_lvl = st.tabs(["File-level views", "Folder-level views"])  

            #populate contents for file level tabs          
            with file_lvl:
                #get filelist from the selected folder  
                st.markdown('Showing processed log files within the selected folder, select any file to view related views')
                filelist = get_file_list(selected_folder, db_obj)
                #selected_file = st.selectbox("select a file.", options=filelist)
                selected_file = draw_fileinfo_grid(filelist)
                if (selected_file is not None):
                    show_diagrams(selected_file, db_obj)
            
            #populate contents for folder level tabs
            with folder_lvl:
                '''**Heatmaps similarity matrix**'''
                #draw similarity heatmap
                draw_similarity_heatmap(selected_folder, db_obj)
        #st.divider()
        selected_file = None

    #Settings Tab
    with settings:
        #currently all settings are dummy and so are disabled. But the plan is to include them in the comming iterations
        #Define columns in the settings tab
        # create a dummy column to make the selectboxes smaller 
        dbsettings, dummy = st.columns([0.5,1], gap="large")
        with dbsettings:               
                        #with st.expander("", expanded=True):
                        st.markdown("#### Database Settings")
                        #with st.expander("Database Settings", expanded=False):
                        st.text_input("Host:", value="Localhost:3306", disabled=True)
                        st.selectbox("Database schema",("smartDelta__PCD",""), disabled=True)
                        st.text_input("Username:", value="root", disabled=True)
                        st.text_input("Password:", value="*******", disabled=True)
                        st.button("Connect", disabled=True)
                        st.divider()
                   
                        #with st.expander("", expanded=True):
                        st.markdown("#### User Settings")     
                        st.write("Currently logged in user: ", user)
                        st.write("logged in since: {0}, {1}".format(date.today(), logged_in_since.strftime('%H:%M %p')))
                        #st.header("User Settings")       
                        st.button("Logout", disabled=True)
        #st.divider()

    #About Tab
    #simple tab containing information about the application
    with about:
        st.markdown('''<font size="2"> <div class="boxed">  Architecture visualization dashboard.  
        Version: 0.1.0          
        Last updated: 06.07.2023  
        [![](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool) </div> </font>''', unsafe_allow_html=True)

def main():
    #read configurations from the config.yaml file
    user_config = get_config(config_file_loc)
    #create a database info object WITH a live db connection that can then be used for executing queries
    db_obj = create_cached_connection(user_config)  
    #start drawing dashboard
    draw_dashboard_main(db_obj)    

if __name__ == '__main__':
    main()