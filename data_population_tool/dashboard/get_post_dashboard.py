import json
import requests
from requests.auth import HTTPBasicAuth

def get_current_dashboard(_get_url, _username, _password):
    print("Getting current dashboard...")
    basic = HTTPBasicAuth(_username, _password)  
    headers = {'Content-Type': 'application/json'}
      
    res = requests.get(_get_url, auth=basic) 
    
    print("fetched current dashboard from Grafana, response was:", res)
    return res   

def post_grafana(_post_url, json_blob, _username, _password):
    basic = HTTPBasicAuth(_username, _password)
  
    headers = {'Content-Type': 'application/json'}
    #TODO: DO this more gracefully, proper error handling and response parsing
    #with open(json_file, "r") as f:
    #    json_data = json.load(f)
    #print(json_data)
    res = requests.post(_post_url, auth=basic, json=json_blob)
    print("post_req_made, response was: ", res)