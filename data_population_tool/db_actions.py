import mysql.connector
from mysql.connector import Error
import pandas as pd


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
            connection = mysql.connector.connect(host= self.host,
                                                    user= self.user,
                                                    password= self.password,
                                                    port= 3306)
            if connection.is_connected():
                db_info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_info)
                #cursor = connection.cursor()
                return connection
        except Error as e:
            print("Error while connecting to MySQL", e)

    def connection_to_db(self, _database):
        #connect to a specific db
        try:
            connection = mysql.connector.connect(host= self.host,
                                                    user= self.user,
                                                    password= self.password,
                                                    database= _database)
            if connection.is_connected():
                db_info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("Connected to database: ", record)
                return connection
        except Error as e:
            print("Error while connecting to MySQL", e)


    def close_conn(self, _dbconn, _cursor):
        if self._dbconn.is_connected():
            _cursor.close()
            _dbconn.close()
            print("MySQL connection is closed...")

"""
def execute_non_query(dbconn, query, database=None):
        #executes a query in the db that does not return data
        if(dbconn.is_connected):
            cursor = dbconn.cursor()
            if(database is not None):  
                query = "USE {0}; {1}".format(database, query)
                cursor.execute(query)
                dbconn.commit()
                #cursor.close()
            else:
                cursor.execute(query)
                dbconn.commit()
            _id = cursor.lastrowid
            return _id
        else:               
            print("Could not connect to mysql db. Please make sure the connection is open...") 
        #return last insert id"""


def execute_non_query(dbconn, query, filelist = None, database=None):
        #executes a query in the db that does not return data
        if(dbconn.is_connected):
            cursor = dbconn.cursor()
            if(database is not None):  
                query = "USE {0}; {1}".format(database, query)
            
            if(filelist is None):
                cursor.execute(query)
            else:
                print("fileid list is not none")
                cursor.executemany(query, filelist)
            dbconn.commit()
            _id = cursor.lastrowid
            return _id
        else:               
            print("Could not connect to mysql db. Please make sure the connection is open...") 
        #return last insert id
        

def execute_query(dbconn, query, database=None):
        #execute query that returns tuples list. Use when there is not need to get dataframes 
        if(dbconn.is_connected):
            cursor = dbconn.cursor(buffered=True)
            if(database is not None):        
                cursor.execute("USE {0}; {1}".format(database, query))
            else:                
                cursor.execute(query)
            res =  cursor.fetchall()
            if (res is not None):
                for row in res:
                    print(row)
            print(res)
            return res
        else:
            print("Could not find an open database conneciton. Please make sure you are connected to the specified db...")

def execute_table(dbconn, query):
    #execute query that returns pandas dataframe 
        if(dbconn.is_connected):
            cursor = dbconn.cursor(buffered=True)
            if(database is not None):        
                cursor.execute("USE {0}; {1}".format(database, query))
            else:                
                cursor.execute(query)
            res =  pd.DataFrame(cursor.fetchall())
            pd.columns = cursor.column_names
            return res
        else:
            print("Could not find an open database conneciton. Please make sure you are connected to the specified db...")

