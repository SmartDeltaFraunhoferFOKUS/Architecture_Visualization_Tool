__author__ = "Fraunhofer Fokus"
__version__ = "0.1.0"

import mysql.connector
from mysql.connector import Error
import pandas as pd
import time

"""
This entire package performs all MySQL database related operations. This involves:
1. Initiating connection with the DB and storing connection objects
2. Performing queries and returning results

"""
class db_adm():
    #use default variables just in case
    host = "localhost"
    database = "smartdelta__pcd"
    user = "root"
    password = "sandman"
    port = 3306
    #number of times to retry connecting to database, if connection in first try fails.
    # retry is more relevant in streamlit since the connection is cached. So if the app does not find db at first then it wont run till the app is restarted again.
    retry = 5

    def __init__(self, _host:str, _user:str, _password:str, _database:str, _port:int):
        """
        Initialize connection to database by using the arguments provided as input to the class

        Args:
        --------
        * _host: database hostname
        * _user: database username
        * _password: database password
        * _database: database name
        * _port: port number
        """
        self.host = _host
        self.user = _user
        self.password = _password
        self.port = _port
        #self.connection = self.get_connection()
        self.connection = self.connection_to_db(_database)

    def get_connection(self):
        """
        Creates a server connection. The connection is non-db specific, it queries using this connection will require to provide database name in the query during query execution

        Returns:
        ------------
        * connection: a connection type object
        """
        #create a connection to connect to the mysql server
        try:
            connection = mysql.connector.connect(host= self.host,
                                                    user= self.user,
                                                    password= self.password,
                                                    port= self.port)
            if connection.is_connected():
                db_info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_info)
                #cursor = connection.cursor()
                return connection
        except Error as e:
            print("Error while connecting to MySQL", e)

    def connection_to_db(self, _database):
        """
        Creates a connection a specific db in the server instance. 
        
        **The connection is db specific, queries using this connection will be executed in the database defined when creating this connection**

        Returns:
        ------------
        * connection: a connection type object
        """
        while(self.retry != 0):
            try:
                connection = mysql.connector.connect(host= self.host,
                                                        user= self.user,
                                                        password= self.password,
                                                        database= _database,
                                                        port= self.port)
                if connection.is_connected():
                    db_info = connection.get_server_info()
                    print("Connected to MySQL Server version ", db_info)
                    cursor = connection.cursor()
                    cursor.execute("select database();")
                    record = cursor.fetchone()
                    print("Connected to database: ", record)
                    return connection
            except Error as e:
                self.retry = self.retry - 1 
                time.sleep(10)
                print("Error while connecting to MySQL...Retrying..", e)
                self.connection_to_db(_database)
        if(self.retry == 0):
            print("Failed to connect to db.")


    def close_conn(self, _dbconn, _cursor):
        """
        Close db connection

        Args:
        * _dbconn: a working database connection
        * _cursor: a cursor
        """
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
        """
        Execute insert and update type queries.

        Args:
        --------
        * dbconn: a working db or server connection
        * query: query string
        * filelist: list of ids to perform the query against. this is a list of tuples [(id1,), (id2,)] or a tuple of form (id,) 
        * database: when this argument is provided, query will be fired in the specifid database

        Returns:
        ------------
        lastrowid entered by the query
        """
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
        """
        Execute query that returns tuples list eg. SELECT statement. Use when there is not need to get dataframes 

        Args:
        --------
        * dbconn: a working db or server connection
        * query: query string
        * database: when this argument is provided, query will be fired in the specifid database

        Returns:
        ------------
        list of tuples as result of query
        """
        
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

def execute_table(dbconn, query, database=None):        
        """
        Execute query to return pandas dataframes

        Args:
        --------
        * dbconn: a working db or server connection
        * query: query string
        * database: when this argument is provided, query will be fired in the specifid database

        Returns:
        ------------
        A pandas dataframe containing the reults of the query
        """

        if(dbconn.is_connected):
            cursor = dbconn.cursor(buffered=True)
            if(database is not None):        
                query = "USE {0}; {1}".format(database, query)

            res =  pd.read_sql(query, dbconn)
            return res
        else:
            print("Could not find an open database conneciton. Please make sure you are connected to the specified db...")

