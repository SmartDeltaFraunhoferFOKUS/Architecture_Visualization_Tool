__author__ = "Fraunhofer Fokus"
__version__ = "0.1.0"

#import streamlit dependencies
import streamlit as st
import streamlit.components.v1 as components



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
#import db related libraries
import mysql.connector
from mysql.connector import Error

#import project internal packages
import db_actions
import settings
import yaml
from core import the_settings_tab, about_tab, dashboard_tab

#database config file location
config_file_loc = r"config.yaml"

#set page layout to wide so that the dashboard takes the whole screen 
st.set_page_config(layout="wide")

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

def get_dashboard_main(db_obj:db_actions.db_adm):
    """
    Draw components on the dashboard. This will draw all three main tabs (dash, settings, about).

    * db_obj: An object that contains database connection.        
    """
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
            dashboard_tab.draw_main_dashboard(db_obj)
    #Settings Tab
    with settings:
        the_settings_tab.draw_settings_tab()
    #About Tab
    #simple tab containing information about the application
    with about:
        about_tab.draw_about_tab(__version__)

def main():
    #read configurations from the config.yaml file
    user_config = get_config(config_file_loc)
    #create a database info object WITH a live db connection that can then be used for executing queries
    db_obj = create_cached_connection(user_config)  
    #start drawing dashboard
    get_dashboard_main(db_obj)    

if __name__ == '__main__':
    main()