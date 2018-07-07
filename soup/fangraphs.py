import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import moneyball.soup.formulas as formulas

from soup import mlb

login_url = 'https://www.fangraphs.com/blogs/wp-login.php?redirect_to=https%3a%2f%2fwww.fangraphs.com%2findex.aspx'
# batters AB>=0
batters_url = 'https://www.fangraphs.com/leaderssplits.aspx?splitArr=&strgroup=game&statgroup=1&startDate=2018-03-01&endDate=2018-11-01&filter=AB%7Cgt%7C0&position=B&statType=player&autoPt=true&players=&pg=0&pageItems=1000&sort=22,1'
# pitchers IP>=0
pitchers_url = 'https://www.fangraphs.com/leaderssplits.aspx?splitArr=&strgroup=game&statgroup=1&startDate=2018-03-01&endDate=2018-11-01&filter=IP%7Cgt%7C0&position=P&statType=player&autoPt=true&players=&pg=0&pageItems=1000&sort=22,1'

bats = '_bat_stats.csv'
pits = '_pit_stats.csv'
fg = '../fangraphs_output'
fg_base = mlb.project_base + fg.split('/')[1] + '/'
roll = '_roll.csv'

def download(email, pw):
    try:
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--start-maximized")
        prefs = {'profile.managed_default_content_settings.images': 2,
                 'download.default_directory' : 'C:\\Users\\lance\\PycharmProjects\\moneyball\\fangraphs_output\\'}
        chromeOptions.add_experimental_option("prefs", prefs)
        chromedriver = 'C:\\Users\\lance\\Downloads\\chromedriver_win32\\chromedriver.exe'
        driver = webdriver.Chrome(chrome_options=chromeOptions, executable_path=chromedriver)
        driver.get('https://www.fangraphs.com/blogs/wp-login.php?redirect_to=https%3a%2f%2fwww.fangraphs.com%2findex.aspx')
        username = driver.find_element_by_id("user_login")
        password = driver.find_element_by_name("pwd")

        username.send_keys(email)
        password.send_keys(pw)

        try:
            #driver.set_page_load_timeout(4)
            page = driver.find_element_by_name("wp-submit").click()
        except TimeoutException:
            pass

        try_get(driver, batters_url)
        export(driver)
        rename(bats)

        try_get(driver, pitchers_url)
        export(driver)
        rename(pits)

    finally:
        driver.quit()

def try_get(driver, url):
    try:
        #driver.set_page_load_timeout(timeout)
        return driver.get(url)
    except TimeoutException:
        pass

def rename(file_suffix):
    for file in os.listdir(fg):
        if 'FanGraphs Splits' in file:
            today = mlb.todayStr()
            src = fg_base + file
            newfile = fg_base + today + file_suffix
            os.rename(src, newfile)

def export(driver):
    driver.find_element_by_id('SplitsLeaderboard_cmdCSV').click()
    time.sleep(10)


def fan_rolls(date):
    for file in os.listdir(fg):
        if date in file:
            fileSuffix = file.split(date)[1]
            df = pd.read_csv(fg_base + date + fileSuffix)
            if bats in file:
                piv_df = rolling_sum(df, 4, 23, date, fileSuffix)
            elif pits in file:
                piv_df = rolling_sum(df, 4, 16, date, fileSuffix)
                piv_df = formulas.DIPS(piv_df)
            else:
                pass
            piv_df.to_csv(fg_base + date + fileSuffix.split('.')[0] + roll, header=True, index=False)

def rolling_sum(df, low, high, date, fileSuffix):
    piv_table = pd.pivot_table(df, index='Date', columns='Name', values=[c for c in df.columns[low:high]])
    piv_table.fillna(0, inplace=True)
    piv_df = piv_table.cumsum().stack()
    piv_df.reset_index(drop=False, inplace=True)
    return piv_df
    #linefang = pd.merge(h_lineups, fangraphs, how='left', left_on=['date', 'name'], right_on=['Date', 'Name'])


if __name__ == '__main__':
    download('Spencer.Levy@Outlook.com', 'Loffa102')
    fan_rolls('2018-07-05')
