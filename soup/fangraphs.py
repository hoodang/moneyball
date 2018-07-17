import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utils.utes as utes
import soup.formulas as formulas
from soup import mlb

login_url = 'https://www.fangraphs.com/blogs/wp-login.php?redirect_to=https%3a%2f%2fwww.fangraphs.com%2findex.aspx'
# batters AB>=0
batters_url = 'https://www.fangraphs.com/leaderssplits.aspx?splitArr=&strgroup=game&statgroup=1&startDate=2018-03-01&endDate=2018-11-01&filter=AB%7Cgt%7C0&position=B&statType=player&autoPt=true&players=&pg=0&pageItems=1000&sort=22,1'
# pitchers IP>=0
pitchers_url = 'https://www.fangraphs.com/leaderssplits.aspx?splitArr=&strgroup=game&statgroup=1&startDate=2018-03-01&endDate=2018-11-01&filter=IP%7Cgt%7C0&position=P&statType=player&autoPt=true&players=&pg=0&pageItems=1000&sort=22,1'

bats = '_bat_stats.csv'
pits = '_pit_stats.csv'
fg = 'fangraphs_output'
chrome_dir = 'chromedriver_win32'
chrome_exe = 'chromedriver.exe'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FANGRAPH_DIR = os.path.join(ROOT_DIR, '..', fg, '')

roll = '_roll.csv'

def download(email, pw):
    try:
        os.makedirs(FANGRAPH_DIR, exist_ok=True)
        os.chmod(FANGRAPH_DIR, 777)
        print(os.listdir(FANGRAPH_DIR))
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--start-maximized")
        prefs = {'profile.managed_default_content_settings.images': 2,
                 'download.default_directory': utes.abPath(FANGRAPH_DIR),
                 'download.directory_upgrade': True,
                 'extensions_to_open': '',
                 'safebrowsing.enabled': True
                 }
        chromeOptions.add_experimental_option("prefs", prefs)
        CHROME_DRIVER = os.path.join(ROOT_DIR, '..', chrome_dir, chrome_exe)
        driver = webdriver.Chrome(chrome_options=chromeOptions, executable_path=CHROME_DRIVER)
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
    for file in os.listdir(FANGRAPH_DIR):
        if 'FanGraphs Splits' in file:
            today = mlb.todayStr()
            src = os.path.join(FANGRAPH_DIR, file)
            newfile = os.path.join(FANGRAPH_DIR, today + file_suffix)
            os.rename(src, newfile)

def export(driver):
    wait = WebDriverWait(driver, 200)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Export Data']")))
    element.click()
    time.sleep(10)


def fan_rolls(date):
    for file in os.listdir(FANGRAPH_DIR):
        if date in file:
            fileSuffix = file.split(date)[1]
            df = pd.read_csv(os.path.join(FANGRAPH_DIR, date + fileSuffix))
            if bats in file:
                piv_df = rolling_sum(df, 4, 23, date, fileSuffix)
            elif pits in file:
                piv_df = rolling_sum(df, 4, 16, date, fileSuffix)
                piv_df = formulas.DIPS(piv_df)
            else:
                pass
            output_location = os.path.join(FANGRAPH_DIR, date + fileSuffix.split('.')[0] + roll)
            piv_df.to_csv(output_location, header=True, index=False)

def rolling_sum(df, low, high, date, fileSuffix):
    piv_table = pd.pivot_table(df, index='Date', columns='Name', values=[c for c in df.columns[low:high]])
    piv_table.fillna(0, inplace=True)
    piv_df = piv_table.cumsum().stack()
    piv_df.reset_index(drop=False, inplace=True)
    return piv_df
    #linefang = pd.merge(h_lineups, fangraphs, how='left', left_on=['date', 'name'], right_on=['Date', 'Name'])


if __name__ == '__main__':
    path = utes.abPath(os.path.join(ROOT_DIR, '..', 'moneyball.properties'))
    utes.load_properties(filepath=path)
    download(os.environ.get('fangraphs_acct'), os.environ.get('fangraphs_pwd'))
    fan_rolls('2018-07-16')
