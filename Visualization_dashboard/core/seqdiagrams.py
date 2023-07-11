import streamlit as st
import streamlit.components.v1 as components
import db_actions

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