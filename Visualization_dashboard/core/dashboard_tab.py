#import streamlit dependencies
import streamlit as st
import streamlit.components.v1 as components

#import bokeh and related extension for streamlit
#from bokeh.plotting import figure, show
#from bokeh.plotting import figure
#from bokeh.models import ColumnDataSource, CustomJS
#from bokeh.models import DataTable, TableColumn, HTMLTemplateFormatter,DateFormatter
#from streamlit_bokeh_events import streamlit_bokeh_events
#from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

from st_aggrid import AgGrid, GridOptionsBuilder
#import python libraries
import numpy as np
import pandas as pd
import json
import re
import json

#import project internal packages
import db_actions
from .heatmaps import *
from .seqdiagrams import draw_sequence_diagram
from .logged_state_diagram import draw_logged_state_diagram
#from .event_map import *
from .event_map_file_lvl import *

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

def get_file_list(folderid: str, db_obj:db_actions.db_adm) -> pd.DataFrame:
    """
    Queries the database to get list of all files and metadata of files

    Args:
    --------
    * folderid: folderid whose files have to be fetched
    * db_obj: An object that contains database connection.  

    Returns:
    -----------
    * records: a pandas dataframe that contains columns: fileid, FileName, CreatedDate, ModifiedDate, SimilarityCount, and filesize FROM tbl_ex_fileinfo and tbl_viz_qualitymetrics for listing in the grid in the UI    
    """
    filelist_dbquery = "SELECT fi.fileid, filename as FileName, createddate as CreatedDate, modifieddate as ModifiedDate, simfilecount as SimilarityCount, filesize FROM tbl_ex_fileinfo fi, tbl_viz_qualitymetrics qm  WHERE fi.folderid = {0} and qm.fileid = fi.fileid".format(folderid)
    records = db_actions.execute_table(db_obj.connection, filelist_dbquery)
    return records
    
def draw_fileinfo_aggrid(pd_dataframe:pd.DataFrame):
    """
    USING AGGRID.:::::> Draws a table that contains details about a file in the dashboard.
    
    Uses bokeh to draw tables. And uses streamlits bokeh events to handle click events to the grid

    Args:
    --------
    * pd_dataframe: A pandas dataframe containing details about a file

    Returns:
    -----------
    * selected_file.iloc[0]: Selected filename when the filelist grid is clicked
    * None: when nothing is selected in the grid 
    """

    # Define sample data
    df = pd.DataFrame(pd_dataframe)

    # Configure grid options using GridOptionsBuilder
    builder = GridOptionsBuilder.from_dataframe(df)
    #builder.configure_default_column(cellStyle={'color': 'black', 'font-size': '12px'}, suppressMenu=True, wrapHeaderText=True, autoHeaderHeight=True)
    builder.configure_default_column(suppressMenu=True, wrapHeaderText=True, autoHeaderHeight=True)
    #builder.configure_pagination(enabled=False)
    #builder.configure_auto_height(autoHeight= True)
    builder.configure_selection(selection_mode='single', use_checkbox=True)
    #builder.configure_pagination(enabled=True, paginationPageSize=5)
    #builder.configure_column('System Name', editable=False)
    builder.configure_column("CreatedDate", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', header_name="Created Date")
    builder.configure_column("ModifiedDate", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', header_name="Modified Date")
    builder.configure_column("SimilarityCount", header_name="Similarity Count")
    builder.configure_column("filesize", header_name="File Size (KB)")
    builder.configure_column("FileName", header_name="File Name")
    grid_options = builder.build()

    return_value = AgGrid(df, gridOptions=grid_options, height=300, width=500)
    if return_value['selected_rows']:
        filename = return_value['selected_rows'][0]['FileName']
        return filename
    else:
        return None

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
    
    #sequence_diagram, heatmap = st.columns([0.5,0.5], gap="medium")                    
    """
    with heatmap:
        #draw heatmap
        st.markdown("**State coverage heatmap**")
        draw_heatmap(selected_file, db_obj)
    with sequence_diagram:
        #draw sequence diagram
        st.markdown("**Run-time view**")
        draw_sequence_diagram(selected_file, db_obj)
    """
    st.markdown("**Logged state diagram**")
    draw_logged_state_diagram(selected_file, db_obj)

def draw_main_dashboard(db_obj:db_actions.db_adm):
    """
    Draw the complete dashboard tab
    """

    #add a blank column on the right to make the selectbox for foldername smaller
    selectbox, blank = st.columns([0.3,0.7], gap="large")

    #get list of processed folders
    folder_list = get_folder_list(db_obj)  
    folder_options = list(zip(folder_list["fid"], folder_list["foldername"]))
    #draw the select box and list the folders within it
    with selectbox:
        selected_folder = st.selectbox("Select a folder to view related dashboard:",options=folder_options, format_func=lambda x: x[1])
        selected_folder_id = selected_folder[0]
    #Create filelevel and folderlevel tabs.
    # file level tab contains all diagrams that are filelevel
    # folder level tab contains all diagrams that are folderlevel
    file_lvl, folder_lvl, event_map = st.tabs(["File-level views", "Folder-level views", "Event Flow Diagram"]) 
    #populate contents for file level tabs          
    with file_lvl:
        #get filelist from the selected folder  
        st.markdown('Showing processed log files within the selected folder, select any file to draw related views')
        filelist = get_file_list(selected_folder_id, db_obj)
        #selected_file = st.selectbox("select a file.", options=filelist)
        selected_file = draw_fileinfo_aggrid(filelist)
        #draw diagrams based on selected files
        if (selected_file is not None):
            show_diagrams(selected_file, db_obj)
            
        #populate contents for folder level tabs
    with folder_lvl:
        '''**Heatmaps similarity matrix**'''
        #draw similarity heatmap
        st.markdown("**Heatmaps similarity matrix**")
        draw_similarity_heatmap(selected_folder_id, db_obj)
    #st.divider()
    selected_file = None
    
    with event_map:
        "Events flow diagram"
        #draw_event_flow_diagram()
        draw_sm_events_map()
