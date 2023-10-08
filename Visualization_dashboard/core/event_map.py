#import streamlit dependencies
import streamlit as st
import streamlit.components.v1 as components

#import subprocess
import subprocess

from enum import Enum
import tempfile
import json

#supported ceps functionalities
class cep_dev(Enum):
    events_mapping = 1

#use ELK header because it is more efficient for larger diagrams. Ref. https://mermaid.js.org/syntax/flowchart.html
mermaid_elk_header = "%%{init: {\"flowchart\": {\"defaultRenderer\": \"elk\"}} }%%"

def draw_sm_events_map():
    """
    Draw a diagram that: Maps the events with the corresponding state machines.
    """
    uploaded_files = st.file_uploader("Choose ceps files", accept_multiple_files=True)
    cmd = ""    
    tmp_dir="/tmp"
    tmp_files = []
    if(len(uploaded_files)>0):
    #with tempfile.TemporaryDirectory() as tmp_dir:
        for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.read()
                filename = uploaded_file.name
                file_path = f'{tmp_dir}/{filename}'
                tmp_files.append(file_path)
                #st.write("filename:", uploaded_file.name)
                #st.write(bytes_data)
                with open(file_path, 'wb') as file:
                    file.write(bytes_data)
        #for tmp_files in tmp_files:
        #    print(f'{tmp_files}')
        #get output from ceps, rightnow, just handle the events map diagram
        mermaid_statements = execute_cmd(tmp_files, cep_dev.events_mapping)
        #st.write(mermaid_statements)
        draw_mermaid_diagram(mermaid_statements)
        
def execute_cmd(filelist:list, cmd_type:cep_dev):
    """
    Execute console cmd in a subprocess.
    
    Args:
        cmd_str (str): console command to execute. Like: $ ceps test.ceps
        cmd_type: what type of operation to perform using ceps.
        
    returns:
        output from ceps execution
    """
    try:
        cmd_str = "ceps "
        for file in filelist:
            cmd_str += f' {file} '
        if(cmd_type == cep_dev.events_mapping):
            ceps_out = extract_events_transitively_and_group(cmd_str)
            return get_mermaid_statement(ceps_out)
        else:
            print("Type not supported")
    except subprocess.CalledProcessError as e:
        st.write(f"Error: {e}")
                
def extract_events_transitively_and_group(cmd_str):
    cmd_str += "./ceps_dev/extract_events_transitively_and_group.ceps"
    print("Executing: {0}".format(cmd_str))
    result = subprocess.check_output(cmd_str, shell=True, text=True)
    print("Output:")
    print(result)
    return result

def get_mermaid_statement(data:str):
    """
    Get mermaid statements from the given data

    Args:
        data (str): data convertible to mermaid statements

    Returns:
        string: mermaid statements
    """
    data=json.loads(data)
    print(f'data to draw: {data}')
    transitions = []
    # Initialize the Mermaid diagram
    mermaid_diagram = "graph TD;\n"

    # Create nodes for state machines
    for component in data["components"]:
        state_machine_name = component["name"]
        mermaid_diagram += f'    {state_machine_name}["{state_machine_name}"];\n'
    # Create edges for events
    for component in data["components"]:
        current_state_machine_name = component["name"]
        print(state_machine_name)
        # Add edges for incoming events
        for event_in in component.get("in_events", []):
            for c1 in data["components"]:    
                state_machine_name = c1["name"]
                if(state_machine_name) != current_state_machine_name:
                    for event_out in c1.get("out_events", []):
                        if(event_out in event_in):
                            tran_tuple = (state_machine_name, current_state_machine_name, event_in)
                            if(tran_tuple not in transitions):
                                transitions.append(tran_tuple)
                                mermaid_diagram += f'    {state_machine_name} -->|{event_in}|{current_state_machine_name};  \n'
        # Add edges for outgoing events    
        for event_out in component.get("out_events", []):
            for c2 in data["components"]: 
                state_machine_name = c2["name"]           
                if(state_machine_name) != current_state_machine_name:
                    for event_in in c2.get("in_events", []):
                        if(event_in in event_out):
                            tran_tuple = (current_state_machine_name, state_machine_name, event_out)
                            if(tran_tuple not in transitions):
                                transitions.append(tran_tuple)
                                mermaid_diagram += f'    {current_state_machine_name} -->|{event_in}|{state_machine_name};  \n'
    return mermaid_diagram

def draw_mermaid_diagram(mermaid_statements):
    """
    Draw mermaid diagram using the given mermaid statements

    Args:
        mermaid_statements (string): mermaid statements
    """
    #define HTML. The java script and the mermaid class is necessary
    html_string = """<script src="https://unpkg.com/mermaid@8.0.0/dist/mermaid.min.js"></script><div class="mermaid">{0}\n{1}</div>""".format(mermaid_elk_header, mermaid_statements)
    print(html_string)
    components.html(html_string, width=800, height=520, scrolling=True) 