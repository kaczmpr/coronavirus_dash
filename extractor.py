import requests
import pandas as pd
from os import path
from datetime import datetime
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

URL_COVID = 'https://corona.lmao.ninja/v2/historical'
URL_COUNTRIES = 'https://restcountries.eu/rest/v2/all'
FILE_PATH = path.abspath(path.join(path.join(path.dirname(__file__),'data','coronavirus.tsv')))
FILE_PATH_COUNTRIES = path.abspath(path.join(path.join(path.dirname(__file__),'data','countries.tsv')))
COUNTRY_MAPPER = {'russia':'russian federation',
                  'bosnia':'bosnia and herzegovina',
                  'taiwan*':'taiwan',
                  'brunei':'brunei darussalam',
                  'diamond princess':'n/a',
                  "cote d'ivoire":'n/a',
                  'north macedonia':'republic of macedonia',
                  'czechia':'czech republic',
                  'moldova':'republic of moldova',
                  's. korea':'korea (republic of)',
                  'venezuela':'venezuela (bolivarian republic of)',
                  'vietnam':'socialist republic of vietnam',
                  'iran':'islamic republic of iran'}

def get_covid_data():
    _requests = requests.get(URL_COVID).json()

    df = pd.DataFrame.from_dict(_requests)
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
    df['country'] = df.country.map(lambda x: str(COUNTRY_MAPPER[x]) if x in COUNTRY_MAPPER.keys() else str(x))


    df.sort_values(by='date', inplace=True)

    df = df.groupby(['date','country']).agg({'cases': 'sum', 'deaths':'sum'}).reset_index()
    df = df.loc[df['cases'] > 100]
    df['day_of_epidemie'] = df.loc[df['cases'] > 0].groupby(['country'])['date'].rank(ascending=True)
    df.dropna(subset=['day_of_epidemie'], inplace=True)
    df['day_of_epidemie'] = df.day_of_epidemie.map(lambda x: int(x))

    df = df.set_index('date')
    df.to_csv(FILE_PATH, encoding='utf8', sep='\t')

def get_country_data():
    _requests = requests.get(URL_COUNTRIES).json()
    df = pd.DataFrame.from_dict(_requests)
    df = df[['name', 'alpha3Code', 'callingCodes', 'altSpellings', 'region', 'population', 'latlng', 'area']]
    df['name_as_list'] = df['name'].map(lambda x: [x])
    df['names'] = df['name_as_list'] + df['altSpellings']
    df['names'] = df['names'].map(lambda x: str(x).casefold().replace('[', '').replace(']', '').replace('\'','').split(','))
    df.to_csv(FILE_PATH_COUNTRIES, encoding='utf8', sep='\t')
    return df


if __name__=='__main__':
    get_country_data()
    get_covid_data()