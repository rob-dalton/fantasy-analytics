""" 
-------------------------------
EXTRACT DATA 
------------------------------- 
author: Rob D 

Module for analyzing fantasy football data

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn
from loadData import get_season_df

# DATA EXTRACTION FUNCTIONS
def get_position_df(position):
    # filter season df by position and team
    df = df_season[(df_season.opponent != "Bye") &
                    (df_season.points != 0) &
                    (df_season.position==position)]
    
    # filter df for columns of interest
    df_position = df[["week", "name", "team", "position", "opponent", "points"]].dropna()
    
    return df_position


def position_for_team(position, team):
    """
    INPUT: String
    RETURN: DataFrame
    
    Finds all players of position that played
    for team.
    
    """
    # filter season df by position and team
    df_position = get_position_df(position)
    df_position_for = df_position[df_position.team==team]
    
    return df_position_for


def position_against_team(position, team):
    """
    INPUT: String
    RETURN: DataFrame
    
    Finds all players of position that played
    against team.
    
    """
    # filter season df by position and opponent
    df_position = get_position_df(position)
    df_position_against = df_position[(df_position.opponent==team) | (df_position.opponent=="@"+team)]
    
    return df_position_against


def points_for_by_week(position, team):
    """
    INPUT: String
    RETURN: Series
    
    Finds sum of points for a position that
    played for a team by week.
    
    """
    # get position for team
    df = position_for_team(position, team)
    
    # get total position points per week
    points = df.groupby(["week", "team", "opponent"]).agg(lambda x: x.sum())
    
    return points.reset_index()[["week", "team", "opponent", "points"]]


def points_against_by_week(position, team):
    """
    INPUT: String
    RETURN: Series
    
    Finds sum of points for players of a position that
    played against a team by week.
    
    """
    # get points against team
    df = position_against_team(position, team)
    
    # get total points against per week
    points = df.groupby(["week", "team"]).agg(lambda x: x.sum())
    points = points.reset_index()[["week", "team", "points"]]
    
    return points.rename(columns={"team": "offense"})


def defenses_against(position):
    """
    INPUT: String
    RETURN: DataFrame
    
    Finds mean and std of total points for a position that
    played against a team by week.
    
    """
    
    # get df by position
    df_position = get_position_df(position)
    
    # get teams
    teams = [opponent for opponent in df_position.opponent.unique() if '@' not in opponent]
    
    # get values per team
    team_values = []
    for team in teams:
        # get total points against team per week
        points_against = points_against_by_week(position, team)
        team_sum = points_against.points.sum()
        team_mean = points_against.points.mean()
        team_sd = points_against.points.std()
        
        team_values.append([team, team_sum, team_mean, team_sd])

    # get dataframe
    df_performance_against = pd.DataFrame(team_values, columns=["team", "points_against", "mean", "std"])
    
    
    return df_performance_against


def epa_for_position(position):

    # get df by position
    df_position = get_position_df(position)

    # get values per team
    team_values = []

    # get teams
    teams = [opponent for opponent in df_position.opponent.unique() if '@' not in opponent]

    for team in teams:
        team_mean = points_for_by_week("WR", team)["points"].mean()
        team_values.append([team, team_mean])

    df = pd.DataFrame(team_values, columns=["team", "mean"]).sort_values("mean")
    df["epa"] = df["mean"] - df["mean"].mean()
    df["position"] = position
    
    return df

# setup global df_season
df_season = get_season_df(1,14)

if __name__=="__main__":
    pass
