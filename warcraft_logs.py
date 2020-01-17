import json
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep
import random
from random import randint
from datetime import date
from time import sleep

# Koelink 2020
# https://github.com/Koelink/warcraft_logs_scraper/
# V0.1.20200117.2

# spreadsheetfile: https://docs.google.com/spreadsheets/d/1NcVmYzOJ-XSx55dQ41WYCURgJDFzsCfhqfTZuU9GbRs/edit#gid=1275718546

def get_json(filename):
    while True:
        try:
            with open(f"{filename}.json") as json_file:
                data = json.load(json_file)
            break
        except:
            print(f"Can't find {filename}.json")
            sleep(10)
    return data


def get_char_id(character):
    try:
        print(f"Getting char_id for {character}")
        endpoint = f'{settings["endpoint"]}rankings/character/{character}/{settings["server_name"]}/{settings["server_location"]}?api_key={secrets["public_key"]}'
        data = requests.get(endpoint).json()
        char_id = data[0]['characterID']
        char_spec = data[0]['spec']
        char_class = data[0]['class']
        print(f"Char_id found for {character}\n")
        return f'{char_id}_{char_spec}_{char_class}'
    except:
        print(f"No char_id found for {character}\n")
        return ""


def get_scores(char_id_spec):
    try:
        sleep(randint(settings["interval_between_scrape_min"],settings["interval_between_scrape_max"]))
        char_id, char_spec, char_class = char_id_spec.split("_")
        char_spec = char_spec.lower()
        headers = {
        "Referer": "https://classic.warcraftlogs.com",
        "X-Requested-With": "XMLHttpRequest"
        }
        if char_spec == "healer":
            char_spec = "hps"
        else:
            char_spec = "dps"
        print(char_id_spec)
        response = requests.get(f'https://classic.warcraftlogs.com/character/rankings-zone/{char_id}/{char_spec}/3/1000/0/3/40/1/Any/rankings/0/0?dpstype=rdps', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        median = soup.find(True, {"class": ["median-perf-avg"]}).get_text().split()[3]
        best_pa = soup.find(True, {"class": ["best-perf-avg"]}).get_text().split()[-1]
        print("best:", best_pa)
        print("median:", median)
        d = date.today()
        return f"{best_pa}_{median}_{d}"
    except:
        return


def manipulate_df(df):
    df['char_id'] = df.apply(lambda x: x['char_id'] if pd.isna(x['char_id']) == False else get_char_id(x['char_name']), axis=1)
    df['char_class'] = df['char_id'].apply(lambda x: x.split("_")[2]if x else "")
    if settings["update_only_once_a_day"]:
        df['high_median'] = df.apply(lambda x: get_scores(x['char_id']) if x['updated'] != str(date.today()) else False, axis=1)
    else:
        df['high_median'] = df.apply(lambda x: get_scores(x['char_id']), axis=1)
    df['best_score'] = df.apply(lambda x: x['high_median'].split("_")[0] if x['high_median'] != False and x["char_class"] != "" else x['best_score'], axis=1)
    df['median_score'] = df.apply(lambda x: x['high_median'].split("_")[1] if x['high_median'] else x['median_score'], axis=1)
    df['updated'] = df.apply(lambda x: x['high_median'].split("_")[2] if x['updated'] != str(date.today()) and x['high_median'] != None else df["updated"], axis=1)
    df['updated'] = df.apply(lambda x: str(date.today()) if len(x['updated']) != 10 else x['updated'], axis=1)
    df = df[["char_id", "updated", "char_name", "char_class", "median_score", "best_score"]]
    return df


def save_df(df):
    while True:
        try:
            df.to_excel(settings["character_file"], index=False)
            print(f"Data saved to {settings['character_file']}")
            break
        except:
            print(f"\nPlease close {settings['character_file']} so I can save your file")
            sleep(5)


def main():
    while True:
        global settings
        global secrets
        settings = get_json("settings")
        secrets = get_json("secrets")
        df = pd.read_excel(settings["character_file"])
        print(df)
        df = manipulate_df(df)
        save_df(df)
        print(df)
        print("Done!")
        print(f"Next check in {settings['hours_sleep']} hours")
        sleep(settings["hours_sleep"]*3600)


if __name__ == "__main__":
    main()

