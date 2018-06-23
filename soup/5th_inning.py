from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

fifth_inning_url = 'https://www.teamrankings.com/mlb/stat/first-5-innings-runs-per-game?date='

def get_inning_stats(soup):
    #table = soup.find('tbody')
    table = soup.findAll('table', {'class': 'tr-table datatable scrollable'})
    df = pd.read_html(str(table), header=0, flavor="bs4")[0]
    print(df.head())

def make_soup(date):
    response = requests.get(fifth_inning_url + date)
    soup = bs(response.content, "html.parser")
    return soup

if __name__ == '__main__':
    soup = make_soup('2018-06-07')
    get_inning_stats(soup)
