#import streamlit dependencies
import streamlit as st
import streamlit.components.v1 as components

#import subprocess
import subprocess

#import python related libs
from enum import Enum
import tempfile
import json
import re
import os
import base64
import zlib

#supported ceps functionalities
class cep_dev(Enum):
    events_mapping = 1

#use ELK header because it is more efficient for larger diagrams. Ref. https://mermaid.js.org/syntax/flowchart.html
mermaid_elk_header = "%%{init: {\"flowchart\": {\"defaultRenderer\": \"elk\"}} }%%"
#mermaid_dagre_header = "%%{init: {\"flowchart\": {\"defaultRenderer\": \"dagre\"}} }%%"
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
        file_state_mch_map, mermaid_statements = execute_cmd(tmp_files, cep_dev.events_mapping)        
        #st.write(mermaid_statements)
        draw_mermaid_diagram(mermaid_statements)
        
def find_keys_by_value(dictionary, target_value):
    """Based on the input value find a list of keys present in the dictionary"""
    keys = []    
    # Iterate through the dictionary items
    for key, values in dictionary.items():
        if target_value in values:
            keys.append(key)    
    return keys

def execute_cmd(filelist:list, cmd_type:cep_dev):
    """
    Execute console cmd in a subprocess.
    
    Args:
        cmd_str (str): console command to execute. Like: $ ceps test.ceps
        cmd_type: what type of operation to perform using ceps.
        
    returns:
        output from ceps execution
    """
    #create a map to store file and corresponding state machine
    file_sm_map = {}
    try:
        cmd_str = "ceps "
        for file in filelist:
            cmd_str += f' {file} '
            execute_pe_cmd = f"ceps {file} --pe"
            s_expr = subprocess.check_output(execute_pe_cmd, shell=True, text=True)
            sm_name = get_sm_name(s_expr)
            file_sm_map[os.path.basename(file)] = sm_name
            print("dict: ",file_sm_map)
        if(cmd_type == cep_dev.events_mapping):
            ceps_out = extract_events_transitively_and_group(cmd_str)
            #st.write(file_sm_map)
            return file_sm_map, get_mermaid_statement(ceps_out, file_sm_map)
        else:
            print("Type not supported")
    except subprocess.CalledProcessError as e:
        st.write(f"Error: {e}")
    
                
def extract_events_transitively_and_group(cmd_str: str):
    """Execute ceps to get events within state machines

    Args:
        cmd_str (str): a json formatted string that maps each state machine to the events they consumed or called. Example: 
                        {
                            "components":
                            [
                                { "name":"S2", "in_events":["E1"], "out_events":["E3","E4","E5"]},
                                { "name":"S0", "in_events":["E9"], "out_events":[]},
                                { "name":"S1", "in_events":["E3"], "out_events":["E1","E2"]}
                            ]
                        }

    Returns:
        string: json formatted events to sm map
    """
    cmd_str += "./ceps_dev/extract_events_transitively_and_group.ceps"
    print("Executing: {0}".format(cmd_str))
    result = subprocess.check_output(cmd_str, shell=True, text=True)
    print("Output:")
    print(result)
    return result


def get_sm_name(s_expr):
    """
    from the given s expression obtained from a single file, create a list of statemachines in that file
    """
    
    #pattern = r'(\(\s*STRUCT\s*\"sm\"\s*\(ID\s*\"(?P<sm_name>\w+)\"\s*)'
    # Use re.findall to extract all matching sections
    #matches = re.search(pattern, s_expr, re.DOTALL)
    #return matches["sm_name"]
    
    sm_names = []
    pattern = r'(\(\s*STRUCT\s*\"sm\"\s*\(ID\s*\"(?P<sm_name>\w+)\"\s*\))'
    matches = re.findall(pattern, s_expr, re.DOTALL)
    for match in matches:
        sm_names.append(match[1]) #2nd element of this tuple is matched value, first is matched pattern 
    return sm_names


def get_mermaid_statement(data:str, sm_file_map:dict):
    """
    Get mermaid statements from the given data

    Args:
        data (str): data convertible to mermaid statements
        sm_events_map (dict): a dict that maps statemachines with files

    Returns:
        string: mermaid statements
    """
    data=json.loads(data)
    print(f'data to draw: {data}')
    transitions = []
    # Initialize the Mermaid diagram
    mermaid_diagram = "graph TD;\n"

    # Create nodes for state machines
    """for component in data["components"]:
        state_machine_name = component["name"]
        filename = find_keys_by_value(sm_file_map, state_machine_name)
        mermaid_diagram += f'\n subgraph {filename[0]} \n'        
        mermaid_diagram += f'    {state_machine_name}["{state_machine_name}"];\n'
        mermaid_diagram += f'  \n end \n '"""
        
    for key, values in sm_file_map.items():
        mermaid_diagram += f'\n subgraph {key} \n'   
        for value in values:
            state_machine_name = value
            byte_code = get_byte_code(key)  
            svg_code_kroki = base64.urlsafe_b64encode(zlib.compress(get_kroki_inp(key), 9)).decode('utf-8')
            mermaid_diagram += f'    {state_machine_name}["{state_machine_name}"];\n'
            #using mermaid 
            #mermaid_diagram += f' click {state_machine_name} "https://mermaid.ink/img/ {byte_code}" _blank;'
            #using kroki (still mermaid but render using kroki)
            mermaid_diagram += f' click {state_machine_name} "https://kroki.io/mermaid/svg/{svg_code_kroki}" _blank;'
        mermaid_diagram += f'  \n end \n '
        
    # Create edges for events
    for component in data["components"]:
        current_state_machine_name = component["name"]
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

def get_byte_code(filename):
    cmd_str = f'ceps  /tmp/{filename} ./ceps_dev/sm2mermaidjs.ceps'
    print("Executing: {0}".format(cmd_str))
    result = subprocess.check_output(cmd_str, shell=True, text=True)
    graphbytes = result.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes) 
    return base64_bytes.decode("ascii") 

def get_kroki_inp(filename):
    cmd_str = f'ceps  /tmp/{filename} ./ceps_dev/sm2mermaidjs.ceps'
    print("Executing: {0}".format(cmd_str))
    result = subprocess.check_output(cmd_str, shell=True, text=True)
    graphbytes = result.encode("ascii")
    return graphbytes

def draw_mermaid_diagram(mermaid_statements):
    """
    Draw mermaid diagram using the given mermaid statements

    Args:
        mermaid_statements (string): mermaid statements
    """
    #define HTML. The java script and the mermaid class is necessary
    html_string = """<script src="https://unpkg.com/mermaid@8.0.0/dist/mermaid.min.js"></script><div class="mermaid">{0}\n{1}</div>""".format(mermaid_elk_header, mermaid_statements)
    #this is the new version of Mermaid, but somehow the ELK header type is not working for this version. 
    #html_string = """<script src="https://cdn.jsdelivr.net/npm/mermaid@10.4.0/dist/mermaid.min.js"></script><div class="mermaid">{0}</div>""".format(mermaid_statements)
    html_string = """<!DOCTYPE html>
                        <html>
                        <head>
                            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.4.0/dist/mermaid.min.js"></script>
                        </head>
                        <body>
                        <!-- Define a script to initialize Mermaid.js -->
                        <script>
                        mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });
                                    function callBack(args) 
                                    {
                                        var result = getIndividualFile(args);
                                        //openResultWindow(result)
                                    };
                                    
                                    function getIndividualFile(arg) {
                                        executeConsoleCommand(arg)
                                        //return 'Python function result: '+ arg ;
                                    }
                                    
                                // Function to open a new window and display the result
                                function openResultWindow(result) {
                                    document.body.innerHTML = '<h1>' + result + '</h1>';
                                    
                                    //var resultWindow = window.open('', '_self');
                                    //resultWindow.document.write('<html><head><title>Mermaid Diagram</title></head><body><h1>' + result + '</h1><img src="' + diagram + '"></body></html>');

                                    //resultWindow.document.close();
                                    };
                                    
                                function executeConsoleCommand(filename) {
                                        if(filename == "s0.ceps")
                                            openResultWindow(filename);
                                        if(filename == "s1.ceps")
                                            openResultWindow(filename,'stateDiagram-v2 [*] --> state1  state1 --> state2   state2 --> [*]');
                                        if(filename == "s2.ceps")
                                            openResultWindow(filename,'stateDiagram-v2 [*] --> s2_state1 s2_state1 --> s2_state2 s2_state2 --> [*]');
                                        if(filename == "s3.ceps")
                                            openResultWindow(filename,'stateDiagram-v2  [*] --> s3_state1 s3_state1 --> s3_state2 s3_state2 --> s3_state3  s3_state3 --> [*]');
                                        if(filename == "s4.ceps")
                                            openResultWindow(filename,'stateDiagram-v2 [*] --> s4_state1 s4_state1 --> s4_state2 s4_state2 --> s4_state3 s4_state3 --> [*]');
                                        if(filename == "client.ceps")
                                            openResultWindow(filename,'stateDiagram-v2   [*] --> RequestConnect  RequestConnect --> ConnectionAccepted  ConnectionAccepted --> [*]');
                                        if(filename == "server.ceps")
                                            openResultWindow(filename,'stateDiagram-v2  [*] --> WaitConnect WaitConnect --> ConnectionAccepted  ConnectionAccepted --> [*]');
                                    }
                        </script>
                        <div class="mermaid">"""+ mermaid_statements + """</div>
                        </body>
                        </html>"""
    
    #print(html_string)
    components.html(html_string, width=1200, height=1500, scrolling=True) 