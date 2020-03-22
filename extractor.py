import requests
import pandas as pd
from datetime import datetime

URL = 'https://corona.lmao.ninja/historical'

requests = requests.get(URL).json()

df = pd.DataFrame.from_dict(requests)
df = df.loc[df['country']!='Country/Region']
df['timeline'] = df.timeline.map(lambda x: dict(x))
df = pd.concat([df.drop(['timeline'], axis=1), df['timeline'].apply(pd.Series)], axis=1)

df_cases = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.cases.apply(pd.Series)], axis=1)
df_cases = pd.melt(df_cases, id_vars=['country','province'], var_name='date', value_name='cases')

df_deaths = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.deaths.apply(pd.Series)], axis=1)
df_deaths = pd.melt(df_deaths, id_vars=['country','province'], var_name='date', value_name='deaths')

df_recovered = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.recovered.apply(pd.Series)], axis=1)
df_recovered = pd.melt(df_recovered, id_vars=['country','province'], var_name='date', value_name='recovered')

df = pd.merge(pd.merge(df_cases, df_deaths, how='left', on=['country', 'province', 'date']), df_recovered, how='left', on=['country', 'province', 'date'])
df['date'] = df.date.map(lambda x: datetime.strptime(x, '%m/%d/%y'))
df['cases'] = df.cases.map(lambda x: int(x))
df['deaths'] = df.deaths.map(lambda x: int(x))
df['recovered'] = df.recovered.map(lambda x: int(x))

df.sort_values(by='date', inplace=True)
df['day_of_epidemie'] = df.loc[df['cases']>0].groupby(['country'])['date'].rank(ascending=True)
df.dropna(subset=['day_of_epidemie'], inplace=True)
df['day_of_epidemie'] = df.day_of_epidemie.map(lambda x: int(x))
df = df.loc[df['country'].isin(['Poland'])]

df = df.set_index('date')
df.to_csv('coronavirus.csv', encoding='utf8')
