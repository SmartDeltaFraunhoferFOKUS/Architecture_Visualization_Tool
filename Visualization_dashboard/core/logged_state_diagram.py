import streamlit as st
import streamlit.components.v1 as components
import base64
import db_actions

def draw_logged_state_diagram(filename: str, db_obj: db_actions.db_adm):
    """
    Query the database based on the currently selected filename and retrieve the mermaid statements and then plot the sequence diagram
    
    Uses html component of streamlit to draw the sequence diagram

    Args:
    --------
    * filename: filename whose sequence diagram will be drawn
    * db_obj: An object that contains database connection.  
    """
    dbquery = "SELECT svg_data FROM tbl_viz_state_diagram s, (select fileid FROM tbl_ex_fileinfo f WHERE filename = '{0}') f WHERE f.fileid = s.fileid".format(filename)
    pd_df = db_actions.execute_table(db_obj.connection, dbquery)
    svg_content = pd_df['svg_data'].apply(lambda x: x.decode('utf-8') if x else None)
    
    if svg_content.empty:
        st.write("No SVG data found for the selected file.")
        return

    svg_data = svg_content.iloc[0]
    
    # Function to convert SVG string to bytes and display it as an image
    def svg_to_image(svg_data):
        svg_bytes = svg_data.encode('utf-8')  # Convert the SVG string to bytes
        svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')  # Encode in base64 to render it as an image
        return f"data:image/svg+xml;base64,{svg_b64}"

    # Convert SVG content to a format suitable for st.image
    svg_image = svg_to_image(svg_data)

    # Display the SVG content using st.image (by passing the data URI)
    #st.markdown("### USM")
    st.image(svg_image, width=500)