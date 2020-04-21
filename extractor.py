import requests
import pandas as pd
from os import path
from datetime import datetime
from analyzer import country_intesection
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

URL_COVID = 'https://corona.lmao.ninja/v2/historical'
URL_COUNTRIES = 'https://restcountries.eu/rest/v2/all'
FILE_PATH = path.abspath(path.join(path.join(path.dirname(__file__),'data','coronavirus.tsv')))
FILE_PATH_COUNTRIES = path.abspath(path.join(path.join(path.dirname(__file__),'data','countries.tsv')))
FILE_PATH_MERGED = path.abspath(path.join(path.join(path.dirname(__file__),'data','merged.tsv')))

# Unfortunately in URL_COVID there is no ISO Country codes, so there is an need to create dictionary - based on country_substract from analyzer
COUNTRY_MAPPER = {'Russia':'russian federation',
                  'Bosnia':'bosnia and herzegovina',
                  'Taiwan*':'taiwan',
                  'Brunei':'brunei darussalam',
                  'Diamond Princess':'n/a',
                  "cote d'ivoire":'n/a',
                  'Macedonia':'republic of macedonia',
                  'Czechia':'czech republic',
                  'Moldova':'republic of moldova',
                  'S. Korea':'korea (republic of)',
                  'Venezuela':'venezuela (bolivarian republic of)',
                  'Vietnam':'socialist republic of vietnam',
                  'Iran':'islamic republic of iran'}

def get_covid_data():
    """Some documentation of function"""
    params = {'lastdays': 'all'}
    _requests = requests.get(URL_COVID, params=params).json()

    df = pd.DataFrame.from_dict(_requests)
    df = df.loc[df['country'] != 'Country/Region']
    df['timeline'] = df.timeline.map(lambda x: dict(x))
    df = pd.concat([df.drop(['timeline'], axis=1), df['timeline'].apply(pd.Series)], axis=1)

    df_cases = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.cases.apply(pd.Series)], axis=1)
    df_cases = pd.melt(df_cases, id_vars=['country', 'province'], var_name='date', value_name='cases')

    df_deaths = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.deaths.apply(pd.Series)], axis=1)
    df_deaths = pd.melt(df_deaths, id_vars=['country', 'province'], var_name='date', value_name='deaths')

    df_recovered = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.cases.apply(pd.Series)], axis=1)
    df_recovered = pd.melt(df_cases, id_vars=['country', 'province'], var_name='date', value_name='recovered')

    df = pd.merge(df_cases, df_deaths, how='left', on=['country', 'province', 'date'])

    df['date'] = df.date.map(lambda x: datetime.strptime(x, '%m/%d/%y'))
    df['cases'] = df.cases.map(lambda x: int(x))
    df['deaths'] = df.deaths.map(lambda x: int(x))
    df['country'] = df.country.map(lambda x: str(COUNTRY_MAPPER[x]).casefold() if x in COUNTRY_MAPPER.keys() else str(x).casefold())

    df.sort_values(by=['country', 'date'], inplace=True)

    df = df.groupby(['date','country']).agg({'cases': 'sum', 'deaths':'sum'}).reset_index()
    df = df.loc[df['cases'] > 100]
    df['day_of_epidemie'] = df.loc[df['cases'] > 0].groupby(['country'])['date'].rank(ascending=True)
    df.dropna(subset=['day_of_epidemie'], inplace=True)
    df['day_of_epidemie'] = df.day_of_epidemie.map(lambda x: int(x))

    df.sort_values(by=['country', 'date'], inplace=True)
    df['new_cases'] = df['cases'].diff()
    df.loc[df.country != df.country.shift(1), 'new_cases'] = 0
    df['new_cases_percent'] = df['new_cases']/(df['cases']-df['new_cases'])*100
    df['new_cases'] = df.new_cases.map(lambda x: int(x))
    df['new_cases_percent'] = df.new_cases_percent.map(lambda x: format(x,'.2f'))
    df.to_csv(FILE_PATH, encoding='utf8', sep='\t', index=False)
    return df

def get_country_data():
    """Some documentation of function"""
    _requests = requests.get(URL_COUNTRIES).json()
    df = pd.DataFrame.from_dict(_requests)
    df = df[['name', 'alpha3Code', 'callingCodes', 'altSpellings', 'region', 'population', 'latlng', 'area']]
    df['name_as_list'] = df['name'].map(lambda x: [x])
    df['names'] = df['name_as_list'] + df['altSpellings']
    df['names'] = df['names'].map(lambda x: list(map(str.lower, x)))
    df.to_csv(FILE_PATH_COUNTRIES, encoding='utf8', sep='\t', index=False)
    return df


if __name__=='__main__':
    df_country = get_country_data()
    df_covid = get_covid_data()

    df_country['country'] = df_country['names'].map(lambda x: country_intesection())
    df_country['country'] = [(set(a).intersection(b)) for a, b in zip(df_country.names, df_country.country)]
    df_country['country'] = df_country['country'].map(lambda x: list(map(str.casefold, x)))
    df_country['country'] = df_country['country'].map(lambda x: x[0] if len(x) > 0 else None)
    df = df_covid.merge(df_country, how='left', on='country')
    df['cases_population_percent'] = df['cases']/df['population']*100
    df['cases_population_percent'] = df['cases_population_percent'].map(lambda x: format(x, '.4f'))
    df = df.set_index('date')

    df.to_csv(FILE_PATH_MERGED, encoding='utf8', sep='\t')