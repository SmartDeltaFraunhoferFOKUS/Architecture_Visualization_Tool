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
    builder.configure_column("SimilarityCount", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', header_name="Similarity Count")
    builder.configure_column("filesize", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', header_name="File Size (KB)")
    builder.configure_column("FileName", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', header_name="File Name")
    grid_options = builder.build()

    return_value = AgGrid(df, gridOptions=grid_options, height=300, width=500)
    if return_value['selected_rows']:
        filename = return_value['selected_rows'][0]['FileName']
        return filename
    else:
         return None

def draw_fileinfo_grid(pd_dataframe:pd.DataFrame):
    """
    USING BOKEH.:::::::> Draws a table that contains details about a file in the dashboard.
    
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

def draw_main_dashboard(db_obj:db_actions.db_adm):
    """
    Draw the complete dashboard tab
    """

    #add a blank column on the right to make the selectbox for foldername smaller
    selectbox, blank = st.columns([0.3,0.7], gap="large")

    #get list of processed folders
    folder_list = get_folder_list(db_obj)  
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
        st.markdown('Showing processed log files within the selected folder, select any file to draw related views')
        filelist = get_file_list(selected_folder, db_obj)
        #selected_file = st.selectbox("select a file.", options=filelist)
        selected_file = draw_fileinfo_aggrid(filelist)
        #draw diagrams based on selected files
        if (selected_file is not None):
            show_diagrams(selected_file, db_obj)
            
        #populate contents for folder level tabs
    with folder_lvl:
        '''**Heatmaps similarity matrix**'''
        #draw similarity heatmap
        draw_similarity_heatmap(selected_folder, db_obj)
    #st.divider()
    selected_file = None

