"""
-----------------------------------------
LOAD DATA
-----------------------------------------

Module for scraping, saving and loading
fantasy football data

"""
import requests
import json
import bs4
import pandas as pd
import numpy as np
import re
import time
import itertools

# VARS
column_names = ["week",
                "name",
                "position",
                "team",
                "opponent",
                "pass_yds",
                "pass_td",
                "int",
                "rush_yds",
                "rush_td",
                "rec_yds",
                "rec_td",
                "fum_td",
                "2pt",
                "fum_lost",
                "points"]


# DATA LOADING FUNCTIONS
def extract_page_data(page_html, week):
    """
    INPUT: BeautifulSoup, int
    RETURN: list
    
    Returns list of player data with week number
    from an NFL Fantasy player rankings page.
    
    """
    # setup vars
    data = []
    
    
    # iterate over players
    for player in page_html:
        values = [week]
        
        # get name, position, team
        td = player.find("td", class_="playerNameAndInfo")
        name = td.find("a").text
        info = td.find("em").text.split("-")
        
        if len(info) == 2:
            position, team = info[0].strip(), info[1].strip()
        else:
            position, team = info[0].strip(), "NA"
      
        # add name, position, team
        values.append(name)
        values.append(position)
        values.append(team)
        
        # get opponent
        opponent = player.find("td", class_="playerOpponent").text
        values.append(opponent)
        
        # get stats
        for stat in player.findAll("td", class_="stat"):
            value = stat.text.strip()
            values.append(0 if value == "-" else float(value))
        
        data.append(values)
        
    return data


def save_week_data(week):
    # setup vars
    pages = range(0,40)
    pages_data = []
    url = "http://fantasy.nfl.com/research/scoringleaders?offset={}&position=O&sort=pts&statCategory=stats&statSeason=2016&statType=weekStats&statWeek={}#researchScoringLeaders=researchScoringLeaders%2C%2Fresearch%2Fscoringleaders%253Foffset%253D1%2526position%253DO%2526sort%253Dpts%2526statCategory%253Dstats%2526statSeason%253D2016%2526statType%253DweekStats%2526statWeek%253D1%2Creplace"
    # iterate over pages
    for page in pages:
        # make request
        offset = page * 25 + 1
        response = requests.get(url.format(offset, week))

        # get html
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        page_html = soup.findAll("tr", class_=re.compile("player"))

        # get data
        page_data = extract_page_data(page_html, week)
        pages_data.append(page_data)
        
        # wait to make next reqeust
        time.sleep(np.random.rand() * 5)
    
    # concatenate pages_data
    week_data = list(itertools.chain.from_iterable(pages_data))
    
    # convert to df
    df_week = pd.DataFrame(week_data, columns=column_names)
    
    # save to file
    df_week.to_pickle("./data/fss_2016_week{}.pkl".format(week))


def get_season_df(start_week, end_week):
    df_season = pd.read_pickle("./data/fss_2016_week{}.pkl".format(start_week))
    weeks = range(start_week+1, end_week+1)
    for week in weeks:
        df_season = df_season.append(pd.read_pickle("./data/fss_2016_week{}.pkl".format(week)))
        
    df_season["points"] = df_season["points"].astype(float)

    return df_season
