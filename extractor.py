import requests
import pandas as pd
from os import path
from datetime import datetime

URL = 'https://corona.lmao.ninja/v2/historical'
FILE_PATH = path.abspath(path.join(path.join(path.dirname(__file__),'data','coronavirus.tsv')))


if __name__=='__main__':
    requests = requests.get(URL).json()

    df = pd.DataFrame.from_dict(requests)
    df = df.loc[df['country'] != 'Country/Region']
    df['timeline'] = df.timeline.map(lambda x: dict(x))
    df = pd.concat([df.drop(['timeline'], axis=1), df['timeline'].apply(pd.Series)], axis=1)

    df_cases = pd.concat([df.drop(['cases', 'deaths'], axis=1), df.cases.apply(pd.Series)], axis=1)
    df_cases = pd.melt(df_cases, id_vars=['country', 'province'], var_name='date', value_name='cases')

    df_deaths = pd.concat([df.drop(['cases', 'deaths'], axis=1), df.deaths.apply(pd.Series)], axis=1)
    df_deaths = pd.melt(df_deaths, id_vars=['country', 'province'], var_name='date', value_name='deaths')

    df = pd.merge(df_cases, df_deaths, how='left', on=['country', 'province', 'date'])

    df['date'] = df.date.map(lambda x: datetime.strptime(x, '%m/%d/%y'))
    df['cases'] = df.cases.map(lambda x: int(x))
    df['deaths'] = df.deaths.map(lambda x: int(x))

    df.sort_values(by='date', inplace=True)

    df = df.groupby(['date','country']).agg({'cases': 'sum', 'deaths':'sum'}).reset_index()
    df = df.loc[df['cases'] > 100]
    df['day_of_epidemie'] = df.loc[df['cases'] > 0].groupby(['country'])['date'].rank(ascending=True)
    df.dropna(subset=['day_of_epidemie'], inplace=True)
    df['day_of_epidemie'] = df.day_of_epidemie.map(lambda x: int(x))

    df = df.set_index('date')
    df.to_csv(FILE_PATH, encoding='utf8', sep='\t')