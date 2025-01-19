import logging
import time
import sqlite3
import time
from PIL import Image
import os
import re
from pathlib import Path
from termcolor import colored
import sys
import traceback
import threading

logger = logging.getLogger("debug_logger")

def log(message, show=None):
    time_now = time.strftime('%H:%M:%S')
    date = time.strftime('%Y-%m-%d')
    if show:
        return logger.info(f"[{date} / {time_now}] {message}")

def traceback_error(detailed=False):
    # Get the traceback object
    exc_type, exc_value, exc_tb = sys.exc_info()
    
    if exc_type is not None:
        # Get the traceback information
        formatted_tb = traceback.format_exception_only(exc_type, exc_value)
        
        # Extract the file name, line number, and error message
        filename = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        error_message = str(exc_value)
        
        # Format the output with static parts colored red
        formatted_message = (
            colored("Error in ", 'light_red') + filename +
            colored(f", line {line_number}: ", 'light_red') + error_message
        )
        
        # Print the formatted short error
        print(formatted_message)
        
        # If 'detailed' is True, print the full traceback
        if detailed:
            # Get the full traceback details
            full_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            # Print the detailed traceback in red
            print(colored(full_traceback, 'light_red'))
        else:
            # Optionally, print an additional message or leave it out
            print('For more details, use the detailed flag.')
        
class SpinnerWithMessage:
    spinner_cycle = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def __init__(self, message):
        self.message = message
        self.stop_running = threading.Event()
        self.spinner_thread = threading.Thread(target=self.init_spinner)
        self.message_lock = threading.Lock()

    def start(self):
        self.spinner_thread.start()

    def stop(self, message, status='success'):
        self.stop_running.set()
        self.spinner_thread.join()
        print('\r' + ' ' * (len(self.message) + 2 + len(self.spinner_cycle[0])), end='\r')
        if status == "success":
            print(colored('✔ ', 'green', attrs=['bold']) + message)
        elif status == 'error':
            print(colored('✘ ', 'red', attrs=['bold']) + message)
        else:
            print("There has been an error. Most likely with \"par: status\"")

    def update(self, new_message):
        with self.message_lock:
            print('\r' + ' ' * (len(self.message) + 2 + len(self.spinner_cycle[0])), end='\r')
            self.message = new_message

    def init_spinner(self):
        while not self.stop_running.is_set():
            for symbol in self.spinner_cycle:
                
                symbol = colored(symbol, 'yellow')
                
                with self.message_lock:
                    print(f'\r{symbol} {self.message}', end='', flush=True)
                time.sleep(0.1)
                if self.stop_running.is_set():
                    break            

def update_content_cache_index():    
    general_db = 'admin_base/general.db'
    
    initial = database.read(general_db, "update_index", "content_update_index")
    new = int(initial[0][0]) + 1
    database.update(general_db, "update_index", "content_update_index", new)

    return initial

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
        
    def read_database(db_path, table):
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {table}"
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
        
def clean_old_hashed_images(image_name, static_root):
    # Get base image name without extension
    base_name = Path(image_name).stem
    
    # Define the pattern to match hashed versions of the image
    pattern = re.compile(rf"{base_name}\.[\w\d]+\.v\d+\.\w+")
    
    # Find all matching hashed versions in the static files directory
    for file_path in Path(static_root).rglob(f"{base_name}.*"):
        if pattern.match(file_path.name):
            os.remove(file_path)              
             
def update_image(image_path, db_path, uploaded_image, field_name, db_table_attr):
    """
    Handles saving and compressing uploaded images.
    Compresses images if they are not PNG; otherwise, saves as-is.
    Checks for existing files with the same name but different formats and deletes them if found.
    Saves the image in the format corresponding to the original image type.
    """
    try:
        # Open the uploaded image
        image = Image.open(uploaded_image)
        image_format = str(image.format.lower())

        # Define the base save path without format
        base_save_path = os.path.join(image_path, field_name)
        
        image_formats = ['jpg', 'jpeg', 'png', 'webp']
        
        # Remove any other versions of image
        for formats in image_formats:
            initial_image_path = f"{base_save_path}.{formats}"
            
            if os.path.exists(initial_image_path):
                os.remove(initial_image_path)
        
        print("Image format: ", image_format)

        # Handle JPG & JPEG images
        if image_format == "jpg" or image_format == "jpeg":
            
            print("here in the jpg section")

            # Save as JPEG
            save_path = f"{base_save_path}.jpg"
            image = image.convert("RGB")  # Ensure it has no alpha channel (JPEG doesn't support transparency)
            image.save(save_path, "JPEG", quality=75, optimize=True)  # Adjust quality as needed
            log(f"Compressed and saved image {field_name} as JPEG at {save_path}.")

            # Save the database with field_name and '.jpg'
            database.update(db_path, db_table_attr, field_name, f"{field_name}.jpg", do_log=False)

        # Handle PNG images
        elif image_format == "png":
            
            print("Got here in PNG section")
                
            print(db_path, db_table_attr, field_name, f"{field_name}.png")

            # Save as PNG without compression
            save_path = f"{base_save_path}.png"
            
            if image.mode == "P" and "transparency" in image.info:
                image = image.convert("RGBA")
    
            image.save(save_path, "PNG")
            log(f"Saved image {field_name} as PNG at {save_path}.")
            
            print('passed this')

            # Save the database with field_name and '.png'
            database.update(db_path, db_table_attr, field_name, f"{field_name}.png", do_log=True)

        # Handle all other types of images
        else:
            print("here in the else section")

            # For any other format, save it with its original format
            existing_path = f"{base_save_path}.{image_format}"
            
            if os.path.exists(existing_path):
                os.remove(existing_path)  # Remove the existing file with the same name and different format
                log(f"Deleted existing file: {existing_path}")

            save_path = f"{base_save_path}.{image_format}"
            image.save(save_path, image_format.upper())  # Save with the original format
            log(f"Saved image {field_name} as {image_format.upper()} at {save_path}.")

            # Save the database with field_name and its respective format
            database.update(db_path, db_table_attr, field_name, f"{field_name}.{image_format}", do_log=False)
            
        print("Updated Image")
        # if settings.DEBUG == False:
        #     clean_old_hashed_images(field_name, image_path)
            
        update_content_cache_index()

    except Exception as e:
        log(f"Error saving image {field_name}: {e}")