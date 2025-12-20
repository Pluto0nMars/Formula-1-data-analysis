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
        team = input("Enter team name (EX -'Red Bull'): ")
        cursor.execute("""
                        SELECT name, nationality, url
                        FROM constructors
                        WHERE name LIKE ?
                        ORDER BY constructorRef ASC
                            """, [team])
        rows = cursor.fetchall()
        if len(rows) == 0:
            print("No Team Found!")
        else:
            for t in rows:
                print(f" {t[0]} ({t[1]}) Team wiki: {t[2]}")
    else:
        print("Invalid choice")


def top_ten_constructors(conn):
    print("")
    cursor = conn.cursor()

    cursor.execute(""" 
                SELECT name, SUM(wins) as total_wins, sum(points) as total_points               
                FROM constructors
                JOIN constructor_standings 
                ON constructors.constructorId = constructor_standings.constructorId
                GROUP BY name
                ORDER BY total_wins desc
                LIMIT 10
            """)
    rows = cursor.fetchall()
    i = 1
    
    for r in rows:
        print(f"{i}. {r[0]}  wins: {r[1]}  {r[2]:.1f}")
        i += 1

def top_20_gp(conn):
    print("")
    cursor = conn.cursor()

    cursor.execute(""" 
                SELECT name, count(*) AS total_gp_wins               
                FROM constructors
                JOIN results
                ON constructors.constructorId = results.constructorId
                GROUP BY name
                ORDER BY total_gp_wins desc
                LIMIT 20
            """)
    rows = cursor.fetchall()
    i = 1
    
    for r in rows:
        print(f"{i}. {r[0]}   race wins: {r[1]}")
        i += 1

def most_driver_championships(conn):
    print("")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT drivers.forename, drivers.surname, COUNT(*) AS championships
        FROM driver_standings
        JOIN RACES ON driver_standings.raceId = races.raceId
        JOIN DRIVERS ON driver_standings.driverId = drivers.driverId
        WHERE driver_standings.position = 1
        AND races.round = (
            SELECT MAX(round) 
            FROM races r2 
            WHERE r2.year = races.year
        )
        GROUP BY drivers.driverId
        ORDER BY championships DESC
        LIMIT 20
        """)
    
    rows = cursor.fetchall()

    for i, r in enumerate(rows, 1):
        print(f"{i}. {r[0]} {r[1]} {r[2]} championships")
    
    print("")

def most_constructor_championships(conn):
    print("")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT constructors.name, COUNT(*) AS CHAMPIONSHIPS
        FROM constructor_standings
        JOIN races ON constructor_standings.raceId = races.raceId
        JOIN constructors ON constructor_standings.constructorId = constructors.constructorId
        WHERE constructor_standings.position = 1
        AND races.round = (
            SELECT MAX(round) 
            FROM races r2 
            WHERE r2.year = races.year
        )
        GROUP BY constructors.constructorId
        ORDER BY championships DESC
        LIMIT 20
        
    """)

    rows = cursor.fetchall()
    for i, r in enumerate(rows, 1):
        print(f"{i}. {r[0]} {r[1]} championships")
    
    print("")
    
def season_points(conn):
    driver_name = input("Enter driver surname: ")
    year = input("Enter the season(year): ")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT drivers.forename, drivers.surname, races.round, races.name, driver_standings.points
    FROM driver_standings
    JOIN drivers ON driver_standings.driverId = drivers.driverId
    JOIN races ON driver_standings.raceId = races.raceId
    WHERE drivers.surname LIKE ? AND races.year LIKE ?
    ORDER BY races.date ASC
    """, [driver_name, year])

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No races found!")
    else:
        print(f"{rows[0][0]} {rows[0][1]} - {year} Season Points Progression:\n")
        
        for r in rows:
            print(f"Round {r[2]}: {r[3]:<30} - {r[4]} points")

    plot = input("\nPlot? (y/n)")

    if plot == 'y':
        round = [r[2] for r in rows]
        points = [r[4] for r in rows]

    
        plt.xlabel("Race Round")
        plt.ylabel("Total Points")

        plt.title(f"{rows[0][0]} {rows[0][1]} - {year} Season")
        plt.plot(round, points, marker='o')

        plt.grid(True)
        plt.show()
    else:
        pass

def two_drivers_comparison(conn):
    driver_1 = input("Enter driver 1 surname: ")
    driver_2 = input("Enter driver 2 surname: ")
    year = input("Enter the season(year): ")

    cursor = conn.cursor()
    cursor.execute("""
        SELECT drivers.forename, drivers.surname, races.round, races.name, driver_standings.points
        FROM driver_standings
        JOIN drivers ON driver_standings.driverId = drivers.driverId
        JOIN races ON driver_standings.raceId = races.raceId
        WHERE drivers.surname LIKE ? AND races.year LIKE ?
        ORDER BY races.date ASC
    """, [driver_1, year])

    driver1_rows = cursor.fetchall()

    cursor.execute("""
        SELECT drivers.forename, drivers.surname, races.round, races.name, driver_standings.points
        FROM driver_standings
        JOIN drivers ON driver_standings.driverId = drivers.driverId
        JOIN races ON driver_standings.raceId = races.raceId
        WHERE drivers.surname LIKE ? AND races.year LIKE ?
        ORDER BY races.date ASC
    """, [driver_2, year])

    driver2_rows = cursor.fetchall()

    if len(driver1_rows) == 0 or len(driver2_rows) == 0:
        print("One or both drivers not found")
        return
    else: 
        print(f"\n{driver1_rows[0][0]} {driver1_rows[0][1]} vs {driver2_rows[0][0]} {driver2_rows[0][1]} - {year}\n")

        for d1, d2 in zip(driver1_rows, driver2_rows):
            print(f"Round {d1[2]}: {d1[3]:<30} | {d1[0]} {d1[1]}: {d1[4]} pts | {d2[0]} {d2[1]}: {d2[4]} pts")

    plot = input("\nPlot? (y/n) ")

    if plot == 'y':
        d1_round = [d[2] for d in driver1_rows]
        d1_points = [d[4] for d in driver1_rows]
        d2_round = [d[2] for d in driver2_rows]
        d2_points = [d[4] for d in driver2_rows]
    else:
        pass

    plt.plot(d1_round, d1_points, marker='o', label=f"{driver1_rows[0][0]} {driver1_rows[0][1]}")
    plt.plot(d2_round, d2_points, marker='s', label=f"{driver2_rows[0][0]} {driver2_rows[0][1]}")
    plt.xlabel("Race Round")
    plt.ylabel("Total Points")
    plt.title(f"{year} - {driver_1} vs. {driver_2}")
    plt.grid(True)
    plt.legend()
    plt.show()


def fast_pit_stop(conn):
    cursor = conn.cursor()
    driver = input("Enter driver surname: ")
    year = input("Enter the season(year): ")

    cursor.execute("""
    SELECT drivers.forename, drivers.surname, 
            AVG(pit_stops.milliseconds) as avg_duration_ms, COUNT(*) as num_stops
    FROM pit_stops
    JOIN drivers ON pit_stops.driverId = drivers.driverId
    JOIN races ON  pit_stops.raceId =  races.raceId
    WHERE races.year LIKE ? AND drivers.surname LIKE  ?
    GROUP BY pit_stops.driverId
    ORDER BY avg_duration_ms ASC
    """, [year, driver])

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("Invalid Year")
    else:
        print(f"\n{year} Average Pit Stop Duration:\n")
        for r in rows:
            avg_seconds = r[2] / 1000
            print(f"{r[0]} {r[1]} : {avg_seconds:.3f} seconds ({r[3]} stops)")

if __name__ == "__main__":
   import_csv() 
   #data = fetch_race_results(2024)
   #print(data)
   #top_ten_constructors(conn)
   #top_20_gp(conn)
   #search_driver_team(conn)
   #most_driver_championships(conn)
   #most_constructor_championships(conn)
   fast_pit_stop(conn)
   #two_drivers_comparison(conn)

   #season_points(conn)   
