import re 
import numpy as np
from os import walk
import os
import intrepret_trace as it
import settings
import pandas as pd
import json
from numpy import dot
from numpy.linalg import norm 
import db_actions
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class create_similarity_heatmap():
    folder_loc = ""
    heat_maps_loc = ""
    sim_heatmaps_loc = ""
    #similarity threshold based on which the metiric similar_files in the database is counted
    similarity_threshold = 95

    def __init__(self, _folder_loc, _heatmaps_loc, _sim_heatmaps_loc) -> None:
        self.folder_loc = _folder_loc
        self.heat_maps_loc = _heatmaps_loc
        self.sim_heatmaps_loc = _sim_heatmaps_loc

    def get_log_folder(self):
        return self.folder_loc
        #return os.path.dirname(root_file_loc)
    
    def get_logs_from_folder(self, log_folder):
        f = []
        for (dirpath, dirnames, filenames) in walk(log_folder):
            for filename in filenames:
                if(filename.endswith(".log")):
                    #f.append(os.path.join(dirpath, filename))
                    f.append(filename)
        return f
    
    def get_states_sequences(self):
        #get all logs
        logs_all = []   
        logs_folder = self.get_log_folder()
        file_list = self.get_logs_from_folder(logs_folder)
        for file in file_list:
            state_seq = open(os.path.join(logs_folder, file), 'r')
            Lines = state_seq.readlines() 
            state_changes_all = []
            for Line in Lines:
                states_trans =[]
                states_trans = Line.split(" ")
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
            #print(state_changes_all)
            logs_all.append(state_changes_all)
        #print(logs_all)
        return (logs_all)

    def get_matrix(self):
        get_all_states = settings.states
        all_state_sequences = self.get_states_sequences()
        all_state_seq_mat = []
        for state_sequences in all_state_sequences:
                state_trans_matrix = []
                for source_state in get_all_states:
                    state_trans_count = []
                    for dest_state in get_all_states:
                            transition = [source_state, dest_state]
                            count= state_sequences.count(transition)
                            state_trans_count.append(count)         
                            #print(transition, count)
                    state_trans_matrix.append(state_trans_count)            
                all_state_seq_mat.append(state_trans_matrix)
        #print(all_state_seq_mat)
        #print("dim:", np.array(all_state_seq_mat).shape)
        return  all_state_seq_mat
    
    def compute_similarity_log(self, pd_frame):
        """
        For each file in the dataframe, count the number of files that have similarity greater than the threshhold value

        Args:
        ------------
        pd_frame: a pandas dataframe that contains named index and columns, with each cell representing similarity value

        Returns:
        -----------
        file_similarity_count: A dictionary of file(key) and its number of similar files (value). 
        """
        sim_count={}
        for index, row in pd_frame.iterrows():  
            similar_files_count=0 
            #for element in row: #gives only 
            for element in row.items():  
                #print(element)      
                #check values
                #only count simiilarty if it is greater than threshhold value(95 percent, currently), 
                # and also not the file itsef. For instance in each row there is also the current file itself        
                if(element[1]*100 > self.similarity_threshold and element[0] != index):
                    similar_files_count= similar_files_count+1
            sim_per_file = {index:similar_files_count}
            sim_count.update(sim_per_file)
        return sim_count
    
    def preprocess_text(self, text):
        """
        Preprocess the text by converting to lowercase,
        removing numbers, and filtering out MAC address-like patterns.
        """
        text = text.lower()
        # Remove numbers
        text = re.sub(r'\b\d+\b', '', text)
        # Remove MAC address-like patterns (e.g., "0:a00:20f::" or "::fe80:0:0:0:ac11")
        text = re.sub(r'([0-9a-fA-F]{1,4}:)+[0-9a-fA-F]{1,4}', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def compute_similarity(self):
        # Read and preprocess all log files
        log_contents = []
        file_names = []
        #Get all .log files from the folder
        log_files = glob.glob(os.path.join(self.get_log_folder(), "*.log"))
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                processed_content = self.preprocess_text(content)
                # Only include files with non-empty content
                if processed_content:
                    log_contents.append(processed_content)
                    file_names.append(os.path.basename(log_file))

        # Check if we have valid content to process
        if not log_contents:
            print("No valid log content found after preprocessing. Please check the log files.")
        else:
            #Compute TF-IDF matrix
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(log_contents)

            #Calculate pair-wise cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            similarity_matrix = np.round(similarity_matrix, 2)
            return similarity_matrix

    def get_similarity_distance(self):
        """
        overall_dist = []
        all_state_seq_mat = self.get_matrix()
        #now file l2 distance between all matrices.
        for state_matrix in all_state_seq_mat:    
            l2_distance_row = []    #contains l2 distance between a single matrix and all other matrices
            for state_matrix_2 in all_state_seq_mat:
                #l2= np.linalg.norm(np.array(state_matrix)-np.array(state_matrix_2))
                #l2_distance_row.append(np.round(l2,2))
                cos_sim = (dot(np.array(state_matrix).flatten(), np.array(state_matrix_2).flatten()))/(norm(np.array(state_matrix).flatten())*norm(np.array(state_matrix_2).flatten()))
                l2_distance_row.append(np.round(cos_sim,2))
            overall_dist.append(l2_distance_row)
        """
        overall_dist = self.compute_similarity()
        print(overall_dist)  
        #create a pandas dataframe
        pd_df = pd.DataFrame(overall_dist)  
        log_folder = self.get_log_folder()
        pd_df.columns= pd_df.index = self.get_logs_from_folder(log_folder)
        #compute the number of similar logs to each log
        sim_count= self.compute_similarity_log(pd_df)        
        similarity_heatmap_blob = self.create_table_json(overall_dist, log_folder)
        return(pd_df, sim_count, similarity_heatmap_blob)


    def create_table_json(self, dataframe, log_folder):
        res = {}
        data = {"z": dataframe.tolist()}
        states =  self.get_logs_from_folder(log_folder)
        res.update(data)
        labels = {"x": states}
        res.update(labels)
        index = {"y": states}
        res.update(index)
        #to add text
        text = {"text": dataframe.tolist()}
        res.update(text)
        add_text = {"texttemplate": "%{text}"}
        res.update(add_text)
        add_color_scheme = {'colorscale':'Viridis'}
        res.update(add_color_scheme)
        #write to file
        #with open("results/heatmaps.json", "w") as f:
        with open(self.sim_heatmaps_loc, "w") as f: 
            json.dump(res, f)
        return res


    def create_table_json_old(self, dataframe):
        b = settings.states
        res = []
        for data in dataframe:
            res.append(dict((zip(b,data))))
            #print(res)
        #with open("results/similarity_heatmaps.json", "w") as f:    
        with open(self.sim_heatmaps_loc, "w") as f:            
            json_blob = json.dumps(res)
            json.dump(res, f)
        #print(json_blob)
        return json_blob
    
def write_sim_map_to_db(folerid, data, logfile_names, db_obj):
    #create string from list
    axis_string = "["
    for logfile in logfile_names:
        axis_string = axis_string + "\"" + logfile + "\"" + ", "
    axis_string = axis_string[:-2] + "]"
    print("axis_sttring....", axis_string)
    #insert to db
    dbquery = "INSERT INTO tbl_viz_simheatmaps (folderid, data, axisinfo) VALUES ({0},'{1}', '{2}')".format(folerid, data, axis_string) 
    db_actions.execute_non_query(db_obj.connection, dbquery)

def write_filesim_value_to_db(file_sim_count_dict: dict, db_obj:db_actions.db_adm):
    for key, value in file_sim_count_dict.items():
        #insert to db
        dbquery = "UPDATE tbl_ex_fileinfo SET simfilecount = {0} WHERE filename = '{1}';".format(value, key) 
        db_actions.execute_non_query(db_obj.connection, dbquery)


if __name__ == '__main__':
    get_sim_heat_map = create_similarity_heatmap(r"C:\Users\sab\Downloads\Vulnerablity\SmartDelta\Akka\samples\poc_new\architecture_visualization_tool\dualstackLogs\elevator\elevator_user_decision_sub2.log")
    res = get_sim_heat_map.get_similarity_distance()
    print(res)
