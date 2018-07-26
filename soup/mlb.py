import re
import time
from datetime import date, timedelta, datetime
from pathlib import Path

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import soup.team_rankings as trank
import utils.emailservice as emailservice
import numpy as np
import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LINEUPS_DIR = os.path.join(ROOT_DIR, '..', 'mlb_lineups_output')
TEAM_RANKING_ODDS_DIR = os.path.join(ROOT_DIR, '..', 'team_rankings_odds')
lineups_base_url = 'https://www.mlb.com/starting-lineups/'

def load_lineups(date):
    soup = make_soup(date)
    matchups = get_matchups(soup)
    lineups = get_lineups(matchups, date)
    return lineups
    #lineups_to_csv(lineups, date)


def make_soup(date):
    response = requests.get(lineups_base_url + date)
    soup = bs(response.content, "html.parser")
    return soup


def get_matchups(soup):
    return soup.findAll('div', {'class': 'starting-lineups__matchup'})

def todayStr():
    return datetime.now().strftime("%Y-%m-%d")

def get_lineups(matchups, date):
    lineups = []
    for m in matchups:
        if m.find(text=re.compile("TBD")) or m.find(text=re.compile("There are no games")):
            continue
        team_names = []
        pitch_list = []
        pitchers = m.findAll('div', {'class': 'starting-lineups__pitcher-summary'})
        teams = m.findAll('a', {'class': 'starting-lineups__team-name--link'})
        for team in teams:
            team_name = team.text.strip()
            team_names.append(team_name)
        for i, pitcher in enumerate(pitchers):
            if i in {0, 2}:
                pitch_dict = get_starting_pitcher(pitchers[i], team_names[0 if i == 0 else 1], date)
                pitch_list.append(pitch_dict)
        away_team_name = team_names[0]
        home_team_name = team_names[1]
        away_team = m.find('ol', {'class': 'starting-lineups__team--away'})
        home_team = m.find('ol', {'class': 'starting-lineups__team--home'})
        away_players = get_starters_list(away_team, away_team_name, date)
        away_players.append(pitch_list[0])
        home_players = get_starters_list(home_team, home_team_name, date)
        home_players.append(pitch_list[1])
        lineups.extend(away_players)
        lineups.extend(home_players)
    return lineups


def get_starters_list(team, team_name, date):
    starters = []
    players_li = team.findAll('li', {'class': 'starting-lineups__player'})
    for i, p in enumerate(players_li):
        p_dict = {}
        p_dict['date'] = date
        p_dict['batting_order'] = i+1
        p_dict['name'] = p.find('a').text.strip()
        p_dict['position'] = p.find('span').text.strip()
        p_dict['team'] = team_name
        #print(p_dict)
        starters.append(p_dict)
    return starters

def get_starting_pitcher(pitcher, team_name, date):
    p_dict = {}
    p_dict['date'] = date
    p_dict['batting_order'] = 10
    p_dict['name'] = pitcher.find('div', {'class': 'starting-lineups__pitcher-name'}).text.strip()
    p_dict['position'] = pitcher.find('span', {'class': 'starting-lineups__pitcher-pitch-hand'}).text.strip()
    p_dict['team'] = team_name
    #print(p_dict)
    return p_dict


def lineups_to_csv(lineups, date):
    cols = list(lineups[0].keys())
    df = pd.DataFrame(lineups, columns=cols)
    df = df.apply(lambda x: x.replace('D-Backs', 'Diamondbacks'))
    os.makedirs(LINEUPS_DIR, exist_ok=True)
    df_csv = df.to_csv(os.path.join(LINEUPS_DIR, str(date) + '_lineups.csv'), header=True, index=False)

def odds_lineups_to_csv(odds_lineups, date):
    # cols = list(odds_lineups[0].keys())
    # df = pd.DataFrame(odds_lineups, columns=cols)
    os.makedirs(TEAM_RANKING_ODDS_DIR, exist_ok=True)
    df_csv = odds_lineups.to_csv(os.path.join(TEAM_RANKING_ODDS_DIR, str(date) + '_odds_lineups.csv'), header=True, index=False)

def get_lineup_history(current_date):
    start = time.time()
    opening_day = date(2018, 3, 29)
    current_date = current_date
    history_lineups = []
    for dt in trank.perdelta(opening_day, current_date, timedelta(days=1)):
        print('date test ' + str(dt))
        history_lineups.extend(load_lineups(str(dt)))
    lineups_to_csv(history_lineups, str(current_date))
    end = time.time()
    print('Lineup History Stopwatch: ' + str(end - start))

def get_odds_lineups(date):
    # Read in historic lineups and odds
    h_lineups = pd.read_csv(os.path.join(LINEUPS_DIR, date + '_lineups.csv'))
    # h_lineups = pd.read_csv('../mlb_lineups_output/' + date + '_fan_lineups.csv')
    # print(h_lineups.columns)
    # #h_lineups = pd.DataFrame(np.concatenate([h_lineups.values], axis=1))
    # print(h_lineups.head(2))
    h_odds = pd.read_csv(os.path.join(TEAM_RANKING_ODDS_DIR, date + '_season_odds.csv'))
    # Flatten the ten batters and positions into single rows by date and team composite keys
    cc = h_lineups.groupby(['date', 'team']).cumcount() + 1
    h_lineups = h_lineups.set_index(['date', 'team', cc]).unstack().sort_index(1, level=1)
    h_lineups.columns = ['_'.join(map(str, i)) for i in h_lineups.columns]
    h_lineups = h_lineups.reset_index()
    # Drop the blank or extraneous columns
    h_lineups.dropna(axis=1, inplace=True)
    h_lineups.drop(list(h_lineups.filter(regex='batting')), axis=1, inplace=True)
    # Get all unique teams (mascots) and add to pipe delimited string as regex to use for substring for join to odds df
    # Ex: "Cubs" in lineups dataset is a substring of "Chicago Cubs" in the other dataset
    pat = "|".join(h_lineups['team'].unique())
    # Insert new column 'Mascot' at index 0 which is mapped to full <city><mascot> notation
    #   from 'Team' column in odds df
    h_odds.insert(0, 'Mascot', h_odds['Team'].str.extract("(" + pat + ')', expand=False))
    # Merge on the new column
    odds_lineups = pd.merge(h_odds, h_lineups, how='left', left_on=['Date', 'Mascot'], right_on=['date', 'team'])
    odds_lineups.drop(['Mascot', 'date'], axis=1, inplace=True)
    odds_lineups = odds_lineups.rename(index=str, columns={'team': 'Mascot'})
    return odds_lineups

def notification(target_dt):
    trank.get_historic_odds()
    final_output(target_dt)
    path = Path('/odds_lineups_output/' + target_dt + '_odds_lineups.csv').resolve().absolute()
    emailservice.send_mail('lancecreath@gmail.com', ['lancecreath@gmail.com', 'spencer.levy@outlook.com'], 'Todays Odds Lineups', 'Lets make some money', [path])

def final_output(target_dt):
    start = time.time()
    trank.get_historic_odds()
    d = target_dt.split('-')
    get_lineup_history(date(int(d[0]), int(d[1].lstrip('0')), int(d[2].lstrip('0'))))
    odds_lineups = get_odds_lineups(target_dt)
    odds_lineups_to_csv(odds_lineups, target_dt)
    end = time.time()
    print('Final Output Stopwatch: ' + str(end - start))

if __name__ == '__main__':
    #   load_lineups('2018-03-29')
    # trank.get_historic_odds()
    # get_lineup_history(date(2018, 7, 18))
    # odds_lineups = get_odds_lineups('2018-06-20')
    # odds_lineups_to_csv(odds_lineups, '2018-06-20')
    # final_output('2018-06-22')
     pathlist = []
    # path = Path('../odds_lineups_output/' + '2018-06-21' + '_odds_lineups.csv').resolve().absolute()
    # print(str(path))
    # pathlist.append(path)
    # emailservice.send_mail('lancecreath@gmail.com', ['spencer.levy@outlook.com'], 'Todays Odds Lineups',
    #                        'Lets make some money', path)

