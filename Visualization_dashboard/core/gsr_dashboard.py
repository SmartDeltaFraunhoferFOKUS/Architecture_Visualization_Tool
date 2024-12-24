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
#from .event_map import *
from .event_map_file_lvl import *

def get_session_list(db_obj:db_actions.db_adm) -> pd.DataFrame:
    """
    Queries the database to get list of all current saved sessions from the db

    Args:
    --------
    * db_obj: An object that contains database connection.  

    Returns:
    -----------
    * records: a pandas dataframe that contains columns: ID, filename, svg_file as svg_file  FROM tbl_ex_similarity_info
    
    """
    dbquery = "SELECT ID, filename, CreatedDate FROM tbl_ex_similarity_info"
    records = db_actions.execute_table(db_obj.connection, dbquery)
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
    builder.configure_column("ID", header_name="ID")
    builder.configure_column("filename",  header_name="Session Name")
    builder.configure_column("CreatedDate", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd', header_name="Created Date")
    grid_options = builder.build()

    return_value = AgGrid(df, gridOptions=grid_options, height=250, width=150)
    if return_value['selected_rows']:
        fileID = return_value['selected_rows'][0]['ID']
        return fileID
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

    #draw sequence diagram
    st.markdown("**Delta view**")
    draw_delta_diagram(selected_file, db_obj)

def draw_delta_diagram(selected_file, db_obj):
    query = f"SELECT svg_data_usm, svg_data_dbsm FROM tbl_ex_similarity_info WHERE ID = {selected_file}"
    svg_data = db_actions.execute_table(db_obj.connection, query)

    if svg_data.empty:
        st.write("No SVG data found for the selected file.")
        return

    svg_data_usm = svg_data['svg_data_usm'].iloc[0]
    svg_data_dbsm = svg_data['svg_data_dbsm'].iloc[0]
    
    # Function to convert SVG string to bytes and display it as an image
    def svg_to_image(svg_data):
        svg_bytes = svg_data.encode('utf-8')  # Convert the SVG string to bytes
        svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')  # Encode in base64 to render it as an image
        return f"data:image/svg+xml;base64,{svg_b64}"

    # Convert SVG content to a format suitable for st.image
    svg_image_usm = svg_to_image(svg_data_usm)
    svg_image_dbsm = svg_to_image(svg_data_dbsm)

    # Display the SVG content using st.image (by passing the data URI)
    st.markdown("### USM")
    st.image(svg_image_usm, width=1500)

    st.markdown("### DBSM")
    st.image(svg_image_dbsm, width=1500)

def draw_main_dashboard(db_obj:db_actions.db_adm):
    """
    Draw the complete dashboard tab
    """    
    #get filelist from the selected folder  
    st.markdown('Showing saved session from GSR processing.')
    filelist = get_session_list(db_obj)
    #selected_file = st.selectbox("select a file.", options=filelist)
    selected_file = draw_fileinfo_aggrid(filelist)
    #draw diagrams based on selected files
    if (selected_file is not None):
            show_diagrams(selected_file, db_obj)         
