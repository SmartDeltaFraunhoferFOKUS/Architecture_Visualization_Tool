__author__ = "Fraunhofer Fokus"
__version__ = "0.1.0"

import psycopg2
import pandas as pd
import time


class db_adm:
    # Use default variables as fallbacks
    host = "localhost"
    database = "smartdelta__pcd"
    user = "root"
    password = "sandman"
    #number of times to retry connecting to database, if connection in first try fails.
    # retry is more relevant in streamlit since the connection is cached. So if the app does not find db at first then it wont run till the app is restarted again.
    retry = 1

    def __init__(self, _host, _user, _password, _database, _port):
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
        #leaving to "return cursor.fetchone()[0] if cursor.rowcount > 0 else None" as above also wont cause any problems but there are errors for non-query execution in console which should not affect anything but lets just check it anyway
        if("returning" in query.lower()):
            return cursor.fetchone()[0]
        else:
            return None
    except Exception as e:
        print(f"Error executing non-query: {e}")
        dbconn.rollback()
    finally:
        if cursor:
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


def execute_table(dbconn, query):
    """
    Executes a query and returns the result as a Pandas DataFrame.

    Args:
    --------
    * dbconn: a working db connection
    * query: query string

    Returns:
    ------------
    A Pandas DataFrame containing the results of the query
    """
    try:
        cursor = dbconn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(data, columns=columns)
    except Exception as e:
        print(f"Error executing query for DataFrame: {e}")
    finally:
        cursor.close()
