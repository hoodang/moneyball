import time

import pandas as pd
import numpy as np

p_cols_in = {'TBF', 'HR', 'BB', 'IBB', 'SO', 'HBP', 'IP', 'ERA', 'FIP', 'X FIP', 'K/9', 'BB/9', 'HR/9'}
p_cols = {'dIBB', '$HP', 'dHP', '$BB', 'dBB', '$SO', 'dSO', '$HR', 'dHR', '$H', 'dH', 'dIP', 'dER', 'DIPS'}

project_base = 'C:/Users/lance/PycharmProjects/moneyball/'

tiny = 0.0000000001

def TB_RC(df):
    df['TB_RC'] = (0.47 * df['1B']) + (0.78 * df['2B']) + (1.09 * df['3B']) + (1.4 * df['HR'])
    return df


def DIPS(pitch_fangraph):
    start = time.time()
    fg = pitch_fangraph
    fg['dIBB'] = fg['TBF'] * .0074
    fg['$HP'] = (fg['HBP'] / fg['TBF']).replace((np.inf, -np.inf), (0, 0)) - fg['IBB']
    fg['dHP'] = fg['$HP'] * fg['TBF'] - fg['dIBB']
    fg['$BB'] = (fg['BB'] - fg['IBB']) / (fg['TBF'] - fg['IBB'] - fg['$HP']).replace((np.inf, -np.inf), (0, 0))
    fg['dBB'] = fg['$BB'] * (fg['TBF'] - fg['dIBB'] - fg['dHP'])
    fg['$SO'] = fg['SO'] / (fg['TBF'] - fg['HBP'] - fg['BB']).replace((np.inf, -np.inf), (0, 0))
    fg['dSO'] = fg['$SO'] * (fg['TBF'] - fg['dBB'] - fg['dHP'])

    fg['$HR'] = fg['HR'] / (fg['TBF'] - fg['HBP'] - fg['BB'])
    fg['dHR'] = fg['$HR'] * (fg['TBF'] - fg['dBB'] - fg['dSO'])
    fg['$H'] = .304396 - (fg['$HR'] * 0.08095) - (fg['$SO'] * 0.04782)
    fg['dH'] = fg['$H'] * (fg['TBF'] - fg['dHR'] - fg['dBB'] - fg['dSO'] - fg['dHP']) + fg['dHR']
    fg['dIP'] = (((fg['TBF'] - fg['dBB'] - fg['dHP'] - fg['dSO'] - fg['dH']) * 1.048) + fg['dSO']) / 3
    fg['dER'] = (fg['dH'] - fg['dHR']) * 0.49674 + (fg['dHR'] * 1.294375) + (fg['dBB'] - fg['dIBB']) * 0.3325 + fg['dIBB'] * 0.0864336 + fg['dHP'] * 0.3077 + (fg['TBF'] - fg['dHP'] - fg['dBB'] - fg['dSO'] - fg['dH']) * -0.082927
    fg['DIPS'] = (fg['dER'] * 9 / fg['IP']).replace((np.inf, -np.inf), (0, 0))
    end = time.time()
    print('Final Output Stopwatch: ' + str(end - start))
    return fg

def read_pit_graphs():
    pfg = pd.read_csv(project_base + 'fangraphs_output/' + '2018-06-28_pit_stats.csv')
    return pfg

def write_pit_graphs(df):
    df.to_csv(project_base + 'fangraphs_output/' + '2018-06-28_calc_pit_fangraphs.csv', header=True, index=False)

if __name__ == '__main__':
    pfg = read_pit_graphs()
    dips = DIPS(pfg)
    write_pit_graphs(dips)
