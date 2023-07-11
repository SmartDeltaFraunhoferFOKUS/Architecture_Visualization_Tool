import json
import requests
from requests.auth import HTTPBasicAuth
from .get_post_dashboard import *

mermaid_file_location_default = r"results/mermaid_log_states.mmd"

#current dashboard json from grafana
json_file_loc_default= r"dashboard/dashboard.json"

#Unique id of an already existing dashboard on Grafana
dashboard_UID = "yZGTzKl4k"
#Grafana URIs
POST_url = 'http://localhost:3000/api/dashboards/db/'
GET_url = "http://localhost:3000/api/dashboards/uid/" + dashboard_UID

get_path = "/api/dashboards/uid/"
post_path = "/api/dashboards/db/"

#Grafana auth
username = "admin"
password = "admin"


def get_mermaid_syntax(file_location):
    if(file_location is None):
            file_location = mermaid_file_location_default

    mermaid_syntax_file = open(file_location, "r")
    #read each line and format it so that it can be written in json.
    #here formatting means removing new lines are replacing then with literal "\n" so that the json later intreprets it as new line
    mermaid_syntax = mermaid_syntax_file.read().replace("\n"," \n ")
    #print("overriding info with :\n", mermaid_syntax)
    return mermaid_syntax

def create_update_dashboard(dash_config, mermaid_file, diagram_type, heat_tbl_blob=None, sim_heat_tbl_blob=None):
    """
    use the mermaid file to create/ update grafance dashboard 

    args:
    --------
    dash_config: dashboard configurations from the YAML file
    mermaid_file: mmd file that is to be visualized
    diagram_type: type of diagram to generate (eg: a sequence diagram or a state machine)

    """
    #get current dashboard from grafana
    response = get_current_dashboard(dash_config.grafana_url + get_path + dash_config.dashboard_uid, dash_config.username, dash_config.password)
    if(response.status_code != 200):
        #respose says resourse not found, but if user has selected to create the resourse then create it
        if(response.json()["message"].lower() == "dashboard not found"):
            print("Dashboard with the given UID not found...")
            if(dash_config.create_dashboard):
                print("Creating a new dashboard based on the json provided in the {0} file...".format(dash_config.base_dashboard_location))
                response = create_dashboard(dash_config)
                if(response.status_code !=200):
                    print("Could not create dashboard....Please check if the settings are correct, and that the dashboard title does not already exist. Response {0}, {1}".format(response, response.content))
                    return
            else:
                return
        else:
            print("There was error while fetching the dashboard from Grafana. Please make sure that the settings in the configuration YAML file are correct and try again.")
            print(response.json())
            return

    #save the json to a file, can be useful for debugging
    with open(json_file_loc_default, "w") as f:
        json.dump(response.json(), f)
    print(response.json())
    #update the current dashboard with a new diagram
    update_dashboard_json(dash_config.grafana_url + post_path, 
                          dash_config.username, 
                          dash_config.password, 
                          mermaid_file_location=mermaid_file, 
                          json_file_loc= json_file_loc_default, 
                          mermaid_diagram_type= diagram_type, 
                          heat_table_blob= heat_tbl_blob, 
                          sim_heat_table_blob = sim_heat_tbl_blob) 

def create_dashboard(dash_config):
    with open(dash_config.base_dashboard_location, "r") as f:
        json_data = json.load(f)
        json_data["dashboard"]["uid"] = dash_config.dashboard_uid
        json_data["dashboard"]["title"] = dash_config.dashboard_title
        #update he UID of the original template with the UID that is given in the config. 
        # The assumption here is that the UID in config if does not exist, user wants to make a dashboard with that UID
        post_grafana(dash_config.grafana_url + post_path, json_data, dash_config.username, dash_config.password)
        print("dashboard created...")
        print("check if dashboard created...")
        response = get_current_dashboard(dash_config.grafana_url + get_path + dash_config.dashboard_uid, dash_config.username, dash_config.password)
        return response

def update_dashboard_json(_post_url, 
                          _username,
                            _password, 
                            mermaid_file_location=None, 
                            mermaid_syntax=None, 
                            json_file_loc=None, 
                            mermaid_diagram_type=None, 
                            heat_table_blob= None, 
                            sim_heat_table_blob = None):   
    if(mermaid_syntax is None):     
        mermaid_syntax = get_mermaid_syntax(mermaid_file_location)    
    #open json to update the diagram
    if(json_file_loc is None):
        json_file_loc = json_file_loc_default

    with open(json_file_loc, "r") as f:
        data = json.load(f) 

    for item in data["dashboard"]["panels"]:  
        print(mermaid_diagram_type)
        print(item["title"].lower())
        script = "let trace1 = \n {0};\n\nreturn {{ data: [trace1] }};"
        #todo: use mermaid diagram type as an enum inplace of a hardcoded string
        if("options" in item and "runtime diagram" in item["title"].lower()):
            #print(item["options"])
            old_content = item["options"]["content"]
            #print("content", old_content)           
            item["options"]["content"] =  mermaid_syntax
            print("sequence diagram found...updated...")
            #if (item["title"].lower()=="sequencediagram"):
            #    print("inc size of the panel...............")
            #    item["gridPos"]= "{\"h\": 8,\"w\": 12,\"x\": 0,\"y\": 8}"
            #break

        #TODO:Remove this panel later
        elif("options" in item and "state coverage heatmap" in item["title"].lower() and heat_table_blob is not None):
            #print("........................................iamin.....")
            #print(item["targets"][0]["contents"])
            
            item["options"]["script"] =  script.format(heat_table_blob)
            print("heatmap found...heatmaps update...")
            #print("heatmap table content:", content_)
            #break

        elif("options" in item and "heatmaps similarity matrix" in item["title"].lower() and sim_heat_table_blob is not None):    
            #print(item["targets"][0]["contents"])
            item["options"]["script"] =  script.format(sim_heat_table_blob)
            print("similarity heatmap found...similarity heatmaps update...")
            #print("heatmap table content:", content_)
            #break

    #print(data)
    
    with open(json_file_loc, 'w') as f:
        json.dump(data, f)
        print("{0} updated...".format(json_file_loc))

    post_grafana(_post_url, data, _username, _password)

if __name__ == '__main__':
    response = get_current_dashboard(GET_url, username, password)
    with open(json_file_loc_default, "w") as f:
        json.dump(response.json(), f)
    update_dashboard_json(POST_url, username, password)