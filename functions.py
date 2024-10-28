import logging
import time
import sqlite3

logger = logging.getLogger("debug_logger")

def log(message):
    time_now = time.strftime('%H:%M:%S')
    date = time.strftime('%Y-%m-%d')
    return logger.info(f"[{date} / {time_now}] {message}")

class database():
    """
    A class for handling basic database operations.
    """
    def write(db_path, table, column, value):
      """
        Insert a value into a specific column of a table.

        Parameters:
        db (object): Database connection object
        cursor (object): Cursor object for executing queries.
        table (str): The name of the table.
        column (str): The name of the column.
        value (str/int/float): The value to be inserted.
      """
      
      db = sqlite3.connect(db_path, check_same_thread=False)
      cursor = db.cursor()
      
      try:
         if type(value) == str:
            query = f'INSERT INTO {table} ({column}) VALUES ("{value}");'

         else:
            query = f'INSERT INTO {table} ({column}) VALUES ({value});'
            
         cursor.execute(query)
         db.commit()
         log(f"Succesfully excuted command {query}")
         return True

      except:
         log(f"Error excuting {query}")
   
    def update(db_path, table, column, new_value, do_log=True):
        """
        Update a value in a specific column of a table.

        Parameters:
        db (object): Database connection object.
        cursor (object): Cursor object for executing queries.
        table (str): The name of the table.
        column (str): The name of the column.
        new_value (str/int/float): The new value to update.
        """
        
        db = sqlite3.connect(db_path, check_same_thread=False)
        cursor = db.cursor()
        
        try:
            query = f"SELECT {column} from {table}"
            cursor.execute(query)
            old_value = cursor.fetchall()
            old_value = old_value[0][0]
            
            if type(new_value) == str:
                query = f"""
                UPDATE {table} 
                SET {column} = '{new_value}' 
                WHERE {column} IS '{old_value}'
                """
                    
            elif type(new_value) == int or type(new_value) == float:
                query = f"""
                UPDATE {table} 
                SET {column} = {new_value} 
                WHERE {column} = {old_value};
                """
                    
            cursor.execute(query)
            db.commit()
            
            if do_log == True:
                log(f"Succesfully excuted command {query}")
            
        except Exception as e:
            log(f"Unexpected error: {e}")
   
    def read(db_path, table, column):
        """
        Read values from a specific column of a table.

        Parameters:
        cursor (object): Cursor object for executing queries.
        table (str): The name of the table.
        column (str): The name of the column.
        """
        
        db = sqlite3.connect(db_path, check_same_thread=False)
        cursor = db.cursor()
        
        try:
            query = f"SELECT {column} from {table}"
            cursor.execute(query)
            value = cursor.fetchall()
            return value
        
        except Exception as e:
            log(f"Unexpected error: {e}")
        
    def read_database(db_path, database):
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {database}"
            logging.debug(f"Executing query: {query}")
            
            cursor.execute(query)
            row = cursor.fetchone()  # Fetch one row assuming there's only one
            
            if row is None:
                logging.info("No data found.")
                return {}
            
            columns = [desc[0] for desc in cursor.description]
            
            # Initialize a dictionary to hold column data
            value_list = {column: value for column, value in zip(columns, row)}
            
            # Close the connection
            conn.close()
            
            return value_list

        except sqlite3.DatabaseError as e:
            log(f"Database error: {e}")
        except Exception as e:
            log(f"Unexpected error: {e}")
            
        finally:
            # Ensure the connection is closed if it was opened
            try:
                conn.close()
            except:
                log("Failed to close the database connection.")