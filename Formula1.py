import sqlite3
import requests 

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

if __name__ == "__main__":
    data = fetch_race_results(2024)
    print(data)
