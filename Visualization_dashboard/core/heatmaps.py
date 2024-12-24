import streamlit as st
import plotly.graph_objs  as go
import db_actions
import json


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

def draw_similarity_heatmap(folderid:str, db_obj: db_actions.db_adm):
    """
    Draw pairwise similarity of all the files within the selected folder in a heatmap
    Args:
    --------
    * folderid: selected folderid. Pairwise similarity between all files from the selected folder will be shown
    * db_obj: An object that contains database connection.

    """  
    dbquery = "SELECT data, axisinfo from tbl_viz_simheatmaps s WHERE s.folderid = {0};".format(folderid)
    dataframe = db_actions.execute_table(db_obj.connection, dbquery)
    
    #plot the heat map. Again, the width and height are from a lot of trials, but they could def. be better
    plotly_graph(json.loads(dataframe["data"][0]), json.loads(dataframe["axisinfo"][0]), 850, 600)