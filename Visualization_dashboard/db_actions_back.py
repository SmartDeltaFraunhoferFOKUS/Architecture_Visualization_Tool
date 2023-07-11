import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st

host = "localhost"
database = "smartdelta__pcd"
user = "root"
password = "sandman"

class db_adm():
    host = "localhost"
    database = "smartdelta__pcd"
    user = "root"
    password = "sandman"

    def __init__(self, _host, _user, _password, _database):
        self.host = _host
        self.user = _user
        self.password = _password
        #self.connection = self.get_connection()
        self.connection = self.connection_to_db(_database)

    def get_connection(self):
        #create a connection to connect to the mysql server
        try:
            connection = st.experimental_connection('mysql', type='sql')
            #if connection.is_connected():
            #    db_info = connection.get_server_info()
            #    print("Connected to MySQL Server version ", db_info)
                #cursor = connection.cursor()
            return connection
        except Error as e:
            print("Error while connecting to MySQL", e)

    def connection_to_db(self, _database):
        #connect to a specific db
        try:
            connection = st.experimental_connection('mysql', type='sql')
            #if connection.is_connected():
            #    db_info = connection.get_server_info()
            #    print("Connected to MySQL Server version ", db_info)
            #    cursor = connection.cursor()
            #    cursor.execute("select database();")
            #    record = cursor.fetchone()
            #    print("Connected to database: ", record)
            return connection
        except Error as e:
            print("Error while connecting to MySQL", e)


    def close_conn(self, _dbconn, _cursor):
        if self._dbconn.is_connected():
            _cursor.close()
            _dbconn.close()
            print("MySQL connection is closed...")

def execute_table(dbconn, query, database=None):
    #execute query that returns pandas dataframe 
        #if(dbconn.is_connected):
        #    cursor = dbconn.cursor(buffered=True)
        #    if(database is not None):        
        #        query = "USE {0}; {1}".format(database, query)

            res =  dbconn.query(query)
            return res
        #else:
        #    print("Could not find an open database conneciton. Please make sure you are connected to the specified db...")

