from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import pytz
import datetime as dt
import os


vegas_base_urls = ['http://www.vegasinsider.com/mlb/odds/las-vegas/run', 'http://www.vegasinsider.com/mlb/odds/las-vegas/run/2']

odds_makers = ['Open', 'Vi Consensus', 'Westgate Superbook', 'MGM Mirage', 'William Hill',
               'Wynn LV', 'CG Technology', 'Stations', 'BetOnline']

def make_soup(url):
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    return soup

def process_odds(soup):
    table = soup.find('table', {'class': 'frodds-data-tbl'})
    rows = table.select('tr')
    full_odds = []
    for r in rows:
        td = r.find('td', {'class': 'viCellBg1 cellTextNorm cellBorderL1'})
        row_list = []
        if td:
            team1_row = {}
            team2_row = {}
            tds = r.findAll('td')
            matchup = tds[0]
            game_time, team1, team2 = parse_td(matchup)
            team1_row['game_time'] = game_time
            team2_row['game_time'] = game_time
            team1_row['team'] = team1
            team2_row['team'] = team2
            tds = tds[1:]
            for i, td in enumerate(tds):
                if 'vertical-middle' not in td.attrs['class'] and not td.find('a', {'title':'BetDSI'}):
                    nope, odds1, odds2 = parse_td(td)
                    team1_row[odds_makers[i]] = odds1
                    team2_row[odds_makers[i]] = odds2
            row_list.append(team1_row)
            row_list.append(team2_row)
        full_odds.extend(row_list)
    df = pd.DataFrame(full_odds, columns=full_odds[0].keys())
    est = pytz.timezone('US/Eastern')
    df.insert(0, 'TimeStamp', pytz.utc.localize(dt.datetime.utcnow(), is_dst=None).astimezone(est).replace(microsecond=0).replace(tzinfo=None))
    return df


def parse_td(td):
    game_time = td.find('span')
    teams = []
    team1 = ''
    team2 = ''
    #if first cell, aka matchup
    if game_time:
        game_time = game_time.text.strip()
        teams = td.findAll('a')
        team1 = teams[0].text.strip()
        team2 = teams[1].text.strip()
    #if odds cell
    else:
        for br in td.findAll('br'):
            #print(str(br.next_sibling.strip()))
            teams.append(str(br.next_sibling.strip()))
        if teams:
            team1 = teams[0]
            team2 = teams[1]

    return game_time, team1, team2

def write_odds(df):
    #add path stuff to check file first, add headers
    '''consider pulling file and finding empties, or just doing a groupby on the
        game time and teams and later finding deltas over time?
        -- or, create an index based on matchup for the calendar day
    '''
    df.to_csv('../vegas_run_odds_output/run_odds.csv', mode='a', header=False)


def create_team_odd_row(team):
    pass

if __name__ == '__main__':
    for url in vegas_base_urls:
        soup = make_soup(url)
        df = process_odds(soup)
        write_odds(df)
