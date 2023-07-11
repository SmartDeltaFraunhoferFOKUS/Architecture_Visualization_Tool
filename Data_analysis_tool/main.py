__author__ = "Fraunhofer Fokus"
__version__ = "0.1.0"

import argparse
from math import fabs
#from tkinter.tix import ACROSSTOP
import display_graph as dp
import os
import dashboard.dashboard as dashboard
import intrepret_trace  as it
import settings
import ceps2diagram as ceps
import seq2diagram as sq
import yaml
import json
from heatmaps import heatmaps as hp
from  heatmaps import similarity_heatmap as sim
from os import walk
import db_actions
import mysql.connector
from mysql.connector import Error
import operator
import datetime

#text_file_location=r"results/output.txt"
#location to save mmd files 
mermaid_formatted_statess_file = r"results/mermaid_states.mmd"
mermaid_formatted_log_file = r"results/mermaid_sequence.mmd"

#dashboard config file location
config_file_loc = r"config/dash_config.yaml"

#header text for mermaid diagram
mermaid_diagram_type_umlstates = "stateDiagram-v2 "
mermaid_diagram_type_umlsequence = "sequenceDiagram "

#get url to get json formatted grafana dashboard
dashboard_uid = "yZGTzKl4k"


def check_files_folder(folderid, dbobj):
    #if files from a folder already exists in db, then remove all of them. This is because:
    #   1. Any file could have been modified in the folder so  need to compute diagrams for all
    
    db_query = "SELECT fileid from tbl_ex_fileinfo WHERE folderid IN ({0})".format(folderid)
    records = db_actions.execute_query(dbobj.connection, db_query)
    print("file in folder:", records)
    if(len(records)>0):
        print("files from input folder detected in db. Removing records", records)
        #db_query = "DELETE FROM tbl_dia_states WHERE fileid = %s"
        #db_actions.execute_non_query(dbconn=dbobj.connection, query=db_query, filelist=records)
        db_query = "DELETE FROM tbl_viz_qualitymetrics WHERE fileid = %s"
        db_actions.execute_non_query(dbconn=dbobj.connection, query=db_query, filelist=records)
        db_query = "DELETE FROM tbl_viz_heatmaps WHERE fileid = %s;"
        db_actions.execute_non_query(dbconn=dbobj.connection, query=db_query, filelist=records)
        db_query = "DELETE FROM tbl_viz_seqdiagram WHERE fileid = %s"
        db_actions.execute_non_query(dbconn=dbobj.connection, query=db_query, filelist=records)
        db_query = "DELETE FROM tbl_ex_fileinfo WHERE fileid = %s"
        db_actions.execute_non_query(dbconn=dbobj.connection, query=db_query, filelist=records)
        db_query = "DELETE FROM tbl_viz_simheatmaps WHERE folderid in ({0})".format(folderid)
        db_actions.execute_non_query(dbconn=dbobj.connection, query=db_query)


def get_file_meta(full_file_path):
    """
    Get metadata of the input file

    args:
    -------
    full_file_path: complete path of the file whose metadata is to be generated

    returns:
    -----------
    meta: dictionary with metadatafield(key) and the metadata(value)
    """
    meta={}
    m_timestamp = os.path.getmtime(full_file_path)
    c_timestamp = os.path.getctime(full_file_path)
    modified_date = datetime.datetime.fromtimestamp(m_timestamp)
    created_date = datetime.datetime.fromtimestamp(c_timestamp)
    meta.update({"modified_date": modified_date, "created_date": created_date})
    return meta

def get_files_from_folder(inp_folder, folderid,  db_obj):
    f = []
    #check if files from same folder already exists in db
    check_files_folder(folderid, db_obj)
    for (dirpath, dirnames, filenames) in walk(inp_folder):
        for filename in filenames:
            if(filename.endswith(".log")):
                #f.append(os.path.join(dirpath, filename))
                #f.append(filename)
                full_file_name = os.path.join(dirpath,filename)
                #print(full_file_name)
                meta = get_file_meta(full_file_name)
                insert_query = "INSERT INTO tbl_ex_fileinfo (filename, filelocation, folderid, createddate,modifieddate) VALUES ('{0}', '{1}', {2}, '{3}', '{4}')".format(filename, full_file_name.replace("\\", "\\\\"), folderid, meta["created_date"], meta["modified_date"])           
                print(insert_query)
                id_inserted = db_actions.execute_non_query(db_obj.connection, insert_query)
                filesize_kb= round(os.path.getsize(full_file_name)/1024,2)
                insert_size_query = "INSERT INTO tbl_viz_qualitymetrics (fileid, filesize) VALUES ({0},{1})".format(id_inserted, filesize_kb)
                db_actions.execute_non_query(db_obj.connection, insert_size_query)
                f.append({id_inserted: full_file_name}) 
    return f


def get_config(config_file_loc):
    """
    Get configuration from the config file

    args:
    -------
    config_file_loc: location of the config file

    returns:
    ----------
    a settings.dashboard_configs object that contains dashboard configurations specified in the config yaml file
    """
    with open(config_file_loc, "r") as stream:
        try:
            user_config = settings.user_configs(yaml.safe_load(stream))
            return user_config 
        except yaml.YAMLError as exc:
            print(exc)

def parseCommandLine():
    """
    Parse the command line. Input and output file specification from the user are parsed.
    Help for the command-line is also supported.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-folder',
                        #type=argparse.FileType('r'),
                        required=True,
                        help='Everything within this folder will be processed for visualization')
    
    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    return parser.parse_args()

def compute_sim_heatmap(folder_loc, folderid, db_obj):
    #generate similarity matrix of heatmaps            
    gen_matrix = sim.create_similarity_heatmap(folder_loc)
    #insert to states db
    #hp.write_states_to_db(settings.states, fileid, db_obj)
    mat_datafram, file_sim_dict, similarity_heatmap_table_blob = gen_matrix.get_similarity_distance()
    sim.write_sim_map_to_db(folderid, list(similarity_heatmap_table_blob.values())[0], list(similarity_heatmap_table_blob.values())[1], db_obj)
    sim.write_filesim_value_to_db(file_sim_count_dict=file_sim_dict, db_obj=db_obj)
    print("generated similarity heatmap:", mat_datafram)

def begin_compute(file_list, folder_loc, folderid, user_config, db_obj):
    for file in file_list:
        #text_file_location = open(os.path.join(folder_loc, file), 'r') 
        fileid = list(file.keys())[0]
        text_file_location = list(file.values())[0]
        file_extension = text_file_location.split('.')[1] 
        mermaid_file_loc = ""
        #TODO: this should be enum
        diagram_type = ""    
        if(file_extension == "ceps"):        
            save_to = r"results/output.txt"
            mermaid_file_loc = mermaid_formatted_statess_file
            #pass the ceps through intrepreter to get the s-experssions
            ceps2diagram = ceps.ceps2diagram()
            ceps2diagram.generate_text_file(text_file_location, save_to)       
            #get mermaid statements
            mermaid_statements =  ceps2diagram.get_statements(text_file_location)       
            print("Finished mermaid statements...")
            #generate mermaid diagram
            diagram_type= mermaid_diagram_type_umlstates
            dp.generate_mermaid_diagram(
                mermaid_diagram_type=diagram_type, 
                mermaid_formatted_file= mermaid_file_loc, 
                mermaid_statements= mermaid_statements)
        elif(file_extension == "log"):
            #generate sequence diagrams
            mermaid_file_loc = mermaid_formatted_log_file
            seq2diagram = sq.seq2diagram()    
            mermaid_statements= seq2diagram.parse_file(text_file_location)
            diagram_type = mermaid_diagram_type_umlsequence
            draw_string = dp.generate_mermaid_diagram(
                mermaid_diagram_type=diagram_type, 
                mermaid_formatted_file= mermaid_file_loc, 
                mermaid_statements= mermaid_statements)
            #insert mermaid statements to db
            dbquery = "INSERT INTO tbl_viz_seqdiagram (fileid, mmd) VALUES ({0},'{1}')".format(fileid, draw_string.replace("\n", "\\\n"))
            db_actions.execute_non_query(db_obj.connection, dbquery)
            #generate heatmaps
            get_heat_map = hp.create_heatmaps(text_file_location)
            pd_dataframe, heatmap_table_blob = get_heat_map.create_heatmaps_frame()
            print("generated heatmap:", pd_dataframe)

            #now insert to heatmaps db. here heatmap_table_blob is a json/dict of form {"z":.... "y":.... "x":..."text":..."colorscale":...}
            hp.write_map_to_db(heatmap_table_blob, settings.states, fileid, db_obj)
            #generate similarity matrix of heatmaps        
            #gen_matrix = hp.similarity_heatmap(text_file_location)
            #mat_datafram, similarity_heatmap_table_blob = gen_matrix.get_similarity_distance()
            #print("generated similarity heatmap:", mat_datafram)          
        else:
            print("File type not supported: {0}. Skipped this file...".format(text_file_location))
        #send the generated data to dashboard for visualization
        #dashboard.create_update_dashboard(user_config, mermaid_file_loc, diagram_type, heat_tbl_blob=heatmap_table_blob, sim_heat_tbl_blob=similarity_heatmap_table_blob)
    
    #compute similarity heatmap from the input folder
    compute_sim_heatmap(folder_loc, folderid, db_obj)

def check_folder_empty(folder_loc):
    folder_empty = True
    #check if folder has log files:
    for (dirpath, dirnames, filenames) in walk(folder_loc):
        for filename in filenames:
            if(filename.endswith(".log")):
                folder_empty = False
                break
    return folder_empty           

def main():
    """
    Start processing the input.
    """
    # Parse the traces    
    args = parseCommandLine()    
    #read dashboard and database config from a yaml file
    user_config = get_config(config_file_loc)
    #create a database connection
    db_obj = db_actions.db_adm(user_config.dbhost, user_config.dbusername, user_config.dbpassword, user_config.dbname)
    #get the type of the file (ceps or log), 
    folder_loc = args.input_folder.strip()
    folder_empty = check_folder_empty(folder_loc)
    if(folder_empty):
        raise Exception("Selected folder does not have any log files. Skipping processing...")

    #insert folder to db
    dbquery = "SELECT folderid from tbl_ex_folderinfo WHERE folderlocation = '{0}'".format(folder_loc.replace("\\", "\\\\"))
    record = db_actions.execute_query(db_obj.connection, dbquery)
    #insert to db if the folder does not already exist
    if(len(record)==0):
        print("New folder detected. Inserting to db.")
        dbquery = "INSERT INTO tbl_ex_folderinfo (foldername, folderlocation) VALUES ('{0}', '{1}')".format(os.path.basename(folder_loc), folder_loc.replace("\\", "\\\\"))
        folderid = db_actions.execute_non_query(db_obj.connection, dbquery)
    else:
        #if the select query returned more than 1 tuples then this means that there are multiple folders of same location in db. 
        if (len(record) > 1):
            raise Exception("Multiple same folder entries found. Database sanity check failed...")
        else:
            #record is a list of tuples from the query, so select the first element of the list and then first element of the tuple
            folderid_list = record[0]
            folderid = folderid_list[0]
    files_list = get_files_from_folder(folder_loc, folderid, db_obj)  
    if(len(files_list) >0):
        begin_compute(files_list, folder_loc, folderid, user_config, db_obj)
    else:
        print("Logs not found inside selected folder...")


if __name__ == '__main__':
    main()