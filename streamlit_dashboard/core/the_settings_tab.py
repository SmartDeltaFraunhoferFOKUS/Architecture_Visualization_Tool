import streamlit as st
from datetime import datetime, timedelta
from datetime import date

#this is just a placeholder for now to show currently signed-in use in the  "settings" tab
user ="User1"

#This is currently a placeholder to show the time the current user logged in. Currently always 1 hr from current time. But later there are big plans XD
logged_in_since = datetime.today() - timedelta(hours=0, minutes=50)

def draw_settings_tab():
    """
    Draw the settings tab
    """
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