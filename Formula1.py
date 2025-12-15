import sqlite3
import pandas as pd
import requests 
import matplotlib.pyplot as plt

conn = sqlite3.connect('f1_data.db')

def import_csv():
    csv_files = [
        'circuits',
        'constructor_results',
        'constructor_standings',
        'constructors',
        'driver_standings',
        'drivers',
        'lap_times',
        'pit_stops',
        'races',
        'results',
        'seasons',
        'sprint_results',
        'status'
    ]

    for file in csv_files:
        try:
            df = pd.read_csv(f'data/{file}.csv')
            df.to_sql(file, conn, if_exists='replace', index=False)
        except Exception as e:
            print(f"Error importing {file}.csv: {e}")

    conn.commit()
    print("All CSVs imported successfully!")

# fetch year for given data set 
# returns a dictionary rather than the given json format
def fetch_race_results(year):
    url = f'http://api.jolpi.ca/ergast/f1/{year}/results.json'
    response = requests.get(url)
    data = response.json()
    return data

#fecth specific rounds (will probably be used most often i think)
def fetch_year_round(year, round_num):
   url = f'http://api.jolpi.ca/ergast/f1/{year}/{round_num}/results.json'
   response = requests.get(url)
   data = response.json()
   return data

#fetch qualifying data (not as important as race results but could be intersting to see)
def fetch_qualifying(year, round_num):
    url = f'http://api.jolpi.ca/ergast/f1/{year}/{round_num}/qualifying.json'
    response = requests.get(url)
    data = response.json()
    return data

#fetch pitstops
def fetch_pitsops(year, round_num):
    url = f'http://api.jolpi.ca/ergast/f1/{year}/{round_num}/pitstops.json'
    response = requests.get(url)
    data = response.json()
    return data


def search_driver_team(conn):
    choice = input("Selct 'd' for diver and 't' for team ")
    print("")
    cursor = conn.cursor()
    
    if choice == 'd':
        driver_name = input("Enter driver surname (use % for wildcard): ")
        cursor.execute("""
            SELECT driverID, driverRef, forename, surname, nationality, dob
            FROM drivers
            WHERE surname LIKE ?
            ORDER BY surname ASC
            """, [driver_name])
        
        rows = cursor.fetchall()
        if len(rows) == 0:
            print("No Drivers Found!")
        else:
            for d in rows:
                print(f" {d[0]}: {d[2]} {d[3]} ({d[4]})")
        
    elif choice == 't':
        pass
    else:
        print("Invalid choice")




if __name__ == "__main__":
   import_csv()
   #data = fetch_race_results(2024)
   #print(data)

   search_driver_team(conn)

   conn.close()
