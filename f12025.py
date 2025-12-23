import Formula1
from Formula1 import fetch_race_results
from Formula1 import fetch_qualifying
import sqlite3

conn = sqlite3.connect('f1_data.db')
#add 2025 data 
def check_2025_data():
    
    data = fetch_race_results(2025)
    races = data['MRData']['RaceTable']['Races']
    print(f"2025 has {len(races)} races in the API")
    for race in races[:3]: 
        print(race)

#race data
def add_2025_races(conn):
    cursor = conn.cursor()
    data = fetch_race_results(2025)
    races = data['MRData']['RaceTable']['Races']


    #parse data and insert into database
    for race in races:
        race_round = race['round']
        circuit_id = race['Circuit']['circuitId']
        race_name = race['raceName']
        race_date = race['date']

        cursor.execute("SELECT raceId FROM races WHERE year = 2025 AND round = ?",[race_round])
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO races(year, round, circuitId, name, date)
                VALUES (2025, ?, ?, ?, ?)
            """, [race_round, circuit_id, race_name, race_date])
            print(f"Added:{race_name}")

    conn.commit()


def add_2025_results(conn):
    cursor = conn.cursor()
    data = fetch_race_results(2025)
    races = data['MRData']['RaceTable']['Races']
    
    for race in races:
        race_round = race['round']
        
        # Get the raceId from your database
        cursor.execute("SELECT raceId FROM races WHERE year = 2025 AND round = ?", [race_round])
        race_row = cursor.fetchone()
        if not race_row:
            continue
        race_id = race_row[0]
        

        for result in race['Results']:
            driver_id = result['Driver']['driverId']
            constructor_id = result['Constructor']['constructorId']
            position = result.get('position', None)
            points = result.get('points', 0)
            grid = result.get('grid', 0)
            laps = result.get('laps', 0)
            status = result.get('status', 'Finished')
            
            #check if a result already exists
            cursor.execute("""
                SELECT resultId FROM results 
                WHERE raceId = ? AND driverId = ?
            """, [race_id, driver_id])
            
            #parse and insert
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO results (raceId, driverId, constructorId, position, points, grid, laps)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [race_id, driver_id, constructor_id, position, points, grid, laps])
        
        print(f"Added results for Round {race_round}")
    
    conn.commit()

def add_2025_qualifying(conn):
    cursor = conn.cursor()

    #need number of rraces in 2025
    max_round = cursor.fetchone()[0]

    if not max_round:
        print("No 2025 races found. Add races first.")
        return
    
    # Parse and insert similar
    for round_num in range(1, max_round + 1):
        data = fetch_qualifying(2025, round_num)
    
    conn.commit()
    
