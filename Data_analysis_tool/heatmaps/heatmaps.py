import re
import intrepret_trace as it
import settings
import pandas as pd
import json
import db_actions
import os 
class create_heatmaps():
    
    results_heatmaps_json_location = ""
    log_file_loc = ""

    def __init__(self, _log_file_loc, heatmaps_json_loca) -> None:
        self.log_file_loc = _log_file_loc
        self.results_heatmaps_json_location = heatmaps_json_loca

    def get_states_sequences(self):
        """
        get a list of state changes from the log file. Each element of the list is a two element tuple, one source and other destination
        """
        state_seq = open(self.log_file_loc, 'r')
        lines = state_seq.readlines()
        state_changes_all = []
        states = []
        for line in lines:
            states_trans =[]
            states_trans = line.split(" ")
            #state_change_in_line = []
            init_state = next_state = ""
            for state in states_trans:
                if(re.match(it.trace_pattern_state, state)):
                    #only select messages that are state changes 
                    m = re.match(it.state_from, state)
                    if(m is not None):
                        init_state = m.group("state_from")
                    m = re.match(it.state_to, state)
                    if(m is not None):
                        next_state = m.group("state_to")     
                    if(len(init_state) >0 and len(next_state)>0):
                        state_changes_all.append([init_state[:-1], next_state[:-1]])
                        if(init_state[:-1] not in states):
                            states.append(init_state[:-1])
                        if(next_state[:-1] not in states):
                            states.append(next_state[:-1])
        #print(state_changes_all)
        return state_changes_all   

    def get_matrix(self):
      get_all_states = states
      state_sequences = self.get_states_sequences()
      state_trans_matrix = []
      for source_state in get_all_states:
            state_trans_count = []
            for dest_state in get_all_states:
                  transition = [source_state, dest_state]
                  count= state_sequences.count(transition)
                  state_trans_count.append(count)         
                  #print(transition, count)
            state_trans_matrix.append(state_trans_count)
      #print(state_trans_matrix)
      return state_trans_matrix
    
    def create_heatmaps_frame(self):
        dataframe = self.get_matrix()
        df = pd.DataFrame(dataframe)
        df.columns= df.index = settings.states
        print("heatmap:", df)
        #TODO: saving as table is not correct
        table_json = self.create_data_table(dataframe)
        return df, table_json
    
    def create_data_table(self, dataframe):
        """
        Create script that is acceptable by plotly, This is in format as below:


            let trace1 = [{
                    z: [[1, 20, 30], [20, 1, 60], [30, 60, 1]],
                    x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                    y: ['Morning', 'Afternoon', 'Evening'],
                    type: 'heatmap'
                    }];

            return { data: trace1 };

        """
        res = {}
        data = {"z": dataframe}
        res.update(data)
        labels = {"x": settings.states}
        res.update(labels)
        index = {"y": settings.states}
        res.update(index)
        #to add text
        text = {"text": dataframe}
        res.update(text)
        add_text = {"texttemplate": "%{text}"}
        res.update(add_text)
        add_color_scheme = {'colorscale':'Viridis'}
        res.update(add_color_scheme)
        #write to file
        with open(self.results_heatmaps_json_location, "w") as f: 
            json.dump(res, f)
        return res
        

    def create_table_json_old(self, dataframe):
        b = settings.states
        res = []
        for data in dataframe:
            res.append(dict((zip(b,data))))
            #print(res)
        with open(self.results_heatmaps_json_location, "w") as f:            
            json_blob = json.dumps(res)
            json.dump(res, f)
        #print(json_blob)
        return json_blob

def write_states_to_db(states, fileid, db_obj):
    #create string from list
    states_string = "["
    for state in states:
        states_string = states_string + "\"" + state + "\"" + ", "
    states_string = states_string[:-1] + "]"
    #insert to db
    dbquery = "INSERT INTO tbl_viz_states (fileid, states) VALUES ({0},'{1}')".format(fileid, states_string) 
    db_actions.execute_non_query(db_obj.connection, dbquery)

def write_map_to_db(jsonblob, states, fileid, db_obj):
    #create string from list
    states_string = "["
    for state in states:
        states_string = states_string + "\"" + state + "\"" + ", "
    states_string = states_string[:-2] + "]" #trim the final comma and space
    print("states_string.....", states_string)
    dbquery = "INSERT INTO tbl_viz_heatmaps (fileid, data, states) VALUES ({0},'{1}', '{2}')".format(fileid, list(jsonblob.values())[0], states_string)            
    db_actions.execute_non_query(db_obj.connection, dbquery)  


if __name__ == '__main__':
    get_heat_map = create_heatmaps(r"C:\Users\sab\Downloads\Vulnerablity\SmartDelta\Akka\samples\poc_heatmaps\logs\calc_log_1.txt")
    res = get_heat_map.create_heatmaps_frame()