__author__ = "Fraunhofer Fokus"
__version__ = "0.1.0"

import psycopg2
#mport mysql.connector
#from mysql.connector import Error
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
        self.database = _database
        self.connection = self.connection_to_db()

    def connection_to_db(self):
        """
        Creates a connection to a specific database in the PostgreSQL server.
        Retries if the connection fails. 

        Returns:
        ------------
        * connection: a connection object
        """
        #here retry is 1 because if connection is not there in first try there wont likely be conditions where app will gain usable connection later
        #but in streamlit since sometimes streamlit takes time just to reconise connection, use retry > 1 but only in streamlit
        while self.retry > 0:
            try:
                connection = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port
                )
                print("Connected to the PostgreSQL Database.")
                return connection
            except Exception as e:
                self.retry -= 1
                time.sleep(5)
                print(f"Error connecting to database. Retrying... ({self.retry} attempts left): {e}")

        raise ConnectionError("Failed to connect to the database after multiple attempts.")

    def close_conn(self):
        """
        Close the database connection.
        """
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("PostgreSQL connection is closed.")


def execute_non_query(dbconn, query, filelist=None):
    """
    Executes INSERT or UPDATE queries.

    Args:
    --------
    * dbconn: a working db connection
    * query: query string
    * filelist: list of tuples to perform the query against

    Returns:
    ------------
    Last row ID entered by the query
    """
    try:
        cursor = dbconn.cursor()
        if filelist is None:
            cursor.execute(query)
        else:
            cursor.executemany(query, filelist)
        dbconn.commit()
        print("Query executed successfully!")
        print("query", query)
        #print("cursor.lastrowid", cursor.fetchone()[0])
        #return cursor.fetchone()[0] if cursor.rowcount > 0 else None
        if("returning" in query.lower()):
            return cursor.fetchone()[0]
        else:
            return None
    except Exception as e:
        print(f"Error executing non-query: {e}")
        dbconn.rollback()
    finally:
        cursor.close()


def execute_query(dbconn, query):
    """
    Executes SELECT queries and returns the result as a list of tuples.

    Args:
    --------
    * dbconn: a working db connection
    * query: query string

    Returns:
    ------------
    List of tuples containing the query results
    """
    try:
        cursor = dbconn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()



"""
def execute_non_query(dbconn, query, database=None):
        #executes a query in the db that does not return data
        if(dbconn.is_connected):
            cursor = dbconn.cursor()
            if(database is not None):  
                query = "{1}".format(database, query)
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


def execute_table(dbconn, query, database=None):        
    try:
        # Check if the connection is open
        if dbconn.closed == 0:
            # Switch database/schema if specified
            if database is not None:
                with dbconn.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {database};")
            
            # Use Pandas to execute the query and fetch results
            df = pd.read_sql(query, dbconn)
            print("Query executed successfully.")
            return df
        else:
            print("Database connection is closed. Please ensure the connection is active.")
            return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

