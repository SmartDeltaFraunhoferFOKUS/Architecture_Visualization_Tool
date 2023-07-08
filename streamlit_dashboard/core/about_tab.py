import streamlit as st

def draw_about_tab(version:str):
    """
    Draw the about tab

    Args:
    -------
    version: version info from the main
    """
    st.markdown('''<font size="2"> <div class="boxed">  Architecture visualization dashboard.  
        Version: {}          
        Last updated: 06.07.2023  
        [![](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/SmartDeltaFraunhoferFOKUS/Architecture_Visualization_Tool) </div> </font>'''.format(version), unsafe_allow_html=True)
