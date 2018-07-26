import ast
import os
from pathlib import Path

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import time


team_base_url = 'https://www.teamrankings.com/mlb/team/' #used for odds
teams_url = 'https://www.teamrankings.com/mlb/teams' #used for team hrefs

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEAM_RANKING_ODDS_DIR = os.path.join(ROOT_DIR, '..', 'team_rankings_odds')

head = {'Date', 'Opponent', 'Result', 'Location', 'W/L', 'Div', 'Run_Line', 'Odds', 'Total', 'Money'}

def get_odds_results(soup):
    #table = soup.find('tbody')
    table = soup.findAll('table', {'class': 'tr-table datatable scrollable'})
    df = pd.read_html(str(table), header=0, flavor="bs4")[0]
    df.columns = df.columns.str.replace(' ', '_')
    df['W/L'].fillna(0, inplace=True)
    df['Div'].fillna(0, inplace=True)
    df.set_index('Date', inplace=True)
    d = datetime.now().strftime("%m/%d")
    df = df.loc[: d].reset_index()
    #print(df.head())
    return df

def make_soup(base, team):
    response = requests.get(base + team)
    soup = bs(response.content, "html.parser")
    return soup

def get_teams_uri_list(soup):
    team_uris = []
    table = soup.find('tbody')
    rows = table.findAll('tr')
    for r in rows:
        a = r.find('td').find('a')
        href = a.attrs['href']
        uri = href.split('/').pop()
        team_uris.append(uri)
    return team_uris

def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta
# for result in perdelta(date(2011, 10, 10), date(2011, 12, 12), timedelta(days=4)):


def runline_calc(rundiff, runline):
    if 'NONE' not in str(rundiff):
        return 1 if ast.literal_eval(str(rundiff)+runline) >= .5 else 0
    else:
        0
def get_historic_odds():
    start = time.time()
    uri_soup = make_soup(teams_url, '')
    uris = get_teams_uri_list(uri_soup)
    # final = pd.DataFrame(columns=head)
    df_list = []
    for u in uris:
        soup = make_soup(team_base_url, u)
        df = get_odds_results(soup)
        thisTeam = ' '.join(l.title() for l in u.split('-'))
        df.insert(1, 'Team', thisTeam)
        resultDf = df['Result'].apply(lambda x: pd.Series(x.split(' ')))
        df.drop(['Result'], axis=1, inplace=True)
        df.insert(3, 'Result', resultDf[0])
        df.insert(4, 'Score', resultDf[1])
        runsDf = resultDf[1].apply(lambda x: pd.Series(x.split('-')))
        df.insert(5, 'Runs', runsDf[0])
        df.insert(6, 'Opponent_Runs', runsDf[1])
        diffDf = df['Score'].apply(lambda x: ast.literal_eval(x) if 'm' not in x else 'NONE')
        df.insert(7, 'Run_Diff', diffDf)
        df['Date'] = df['Date'].map(lambda d: pd.to_datetime(str(datetime.now().year) + '-' + d.replace('/', '-')).strftime("%Y-%m-%d"))
        #df.set_index('Date', inplace=True)
        df_list.append(df)
    final = pd.concat(df_list).sort_values('Date')#.set_index('Date')
    final['Run_Line_Cover'] = list(map(runline_calc, final['Run_Diff'], final['Run_Line']))
    date = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(TEAM_RANKING_ODDS_DIR, exist_ok=True)
    df_csv = final.to_csv(os.path.join(TEAM_RANKING_ODDS_DIR, date + '_season_odds.csv'),
        header=True, index=False)
    end = time.time()
    print('Odds History Stopwatch: ' + str(end - start))

if __name__ == '__main__':
    get_historic_odds()


