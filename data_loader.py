import pandas as pd
import sqlite3

# Define the database name
DB_NAME = 'college_cutoffs.db'
TABLE_NAME = 'cutoffs'
CSV_FILE = 'CollegeCutoffs.csv' 

def create_db_and_load_data():
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(CSV_FILE)
        
        # Connect to SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_NAME)
        
        # Write the dataframe to an SQL table
        # if_exists='replace' means it will overwrite any existing table
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"Data successfully loaded from {CSV_FILE} into SQLite database {DB_NAME} in table {TABLE_NAME}.")
        
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found. Please create the CSV file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Make sure your CollegeCutoffs.csv file is in the same directory
    # Then run this script: python data_loader.py
    create_db_and_load_data()