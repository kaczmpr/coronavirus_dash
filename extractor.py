import requests
import pandas as pd
import logging
from os import path
from datetime import datetime
from analyzer import country_intesection


URL_COVID = 'https://corona.lmao.ninja/v2/historical'
URL_COUNTRIES = 'https://restcountries.eu/rest/v2/all'
URL_POLAND = 'https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Poland'
PROJECT_PATH = path.abspath(path.dirname(__file__))
FILE_PATH_CORONAVIRUS = path.abspath(path.join(PROJECT_PATH, 'data','coronavirus.tsv'))
FILE_PATH_COUNTRIES = path.abspath(path.join(PROJECT_PATH, 'data','countries.tsv'))
FILE_PATH_WORLD = path.abspath(path.join(PROJECT_PATH, 'data','world.tsv'))
FILE_PATH_POLAND = path.abspath(path.join(PROJECT_PATH, 'data','poland.tsv'))

# In URL_COVID there is no ISO Country codes, so there is an need to create dictionary - based on country_substract
# from analyzer
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

# Create logger
logger = logging.getLogger('extractor')
handler = logging.FileHandler('extractor.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def get_covid_data():
    """Handling with rest api and return data frame with coivd data"""
    logger.info('Download data from {url}'.format(url=URL_COVID))
    params = {'lastdays': 'all'}
    try:
        _requests = requests.get(URL_COVID, params=params).json()
    except Exception as e:
        logger.exception(e)

    df = pd.DataFrame.from_dict(_requests)
    df = df.loc[df['country'] != 'Country/Region']
    df['timeline'] = df.timeline.map(lambda x: dict(x))
    df = pd.concat([df.drop(['timeline'], axis=1), df['timeline'].apply(pd.Series)], axis=1)

    df_cases = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.cases.apply(pd.Series)], axis=1)
    df_cases = pd.melt(df_cases, id_vars=['country', 'province'], var_name='date', value_name='cases')

    df_deaths = pd.concat([df.drop(['cases', 'deaths', 'recovered'], axis=1), df.deaths.apply(pd.Series)], axis=1)
    df_deaths = pd.melt(df_deaths, id_vars=['country', 'province'], var_name='date', value_name='deaths')

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
    df.to_csv(FILE_PATH_CORONAVIRUS, encoding='utf8', sep='\t', index=False)
    logger.info('Successful saved data from {url}'.format(url=URL_COVID))
    return df


def get_country_data():
    """Handling with REST API and return data frame with country data"""
    logger.info('Download data from {url}'.format(url=URL_COUNTRIES))
    try:
        _requests = requests.get(URL_COUNTRIES).json()
    except Exception as e:
        logger.exception(e)
    df = pd.DataFrame.from_dict(_requests)
    df = df[['name', 'alpha3Code', 'callingCodes', 'altSpellings', 'region', 'population', 'latlng', 'area']]
    df['name_as_list'] = df['name'].map(lambda x: [x])
    df['names'] = df['name_as_list'] + df['altSpellings']
    df['names'] = df['names'].map(lambda x: list(map(str.lower, x)))
    df.to_csv(FILE_PATH_COUNTRIES, encoding='utf8', sep='\t', index=False)
    logger.info('Successful saved data from {url}'.format(url=URL_COUNTRIES))
    return df


def switch_header_row(df):
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    logger.info('Switch header row function successful executed')
    return df


def clean_header_voivodeship(df):
    columns = dict()
    for name in df.columns:
        if name not in ('Date (CET)', 'Poland daily', 'Poland total', 'Sources'):
            columns.update({name: name.split('(')[1].split(')')[0]})
            if ';' in name:
                columns.update({name: name.split(';')[0].split('(')[1]})
        else:
            columns.update({name: name})
            if '(' in name:
                columns.update({name: name.split('(')[0].replace(' ','')})
            if 'Poland' in name:
                columns.update({name: name.split()[1]})
    df.rename(columns=columns, inplace=True)
    df.drop(columns=['Sources'], inplace=True)
    logger.info('Clean header function successful executed')
    return df


def get_poland_voivodeship_iso():
    data = {'Voivodeship': ['dolnośląskie', 'kujawsko-pomorskie', 'lubuskie', 'łódzkie', 'lubelskie', 'małopolskie',
                            'mazowieckie', 'opolskie', 'podlaskie', 'podkarpackie', 'pomorskie', 'świętokrzyskie',
                            'śląskie', 'warmińsko-mazurskie', 'wielkopolskie', 'zachodniopomorskie'],
            'iso_3166-1': ['DS', 'KP', 'LB', 'LD', 'LU', 'MA', 'MZ', 'OP', 'PD', 'PK', 'PM', 'SK', 'SL', 'WN', 'WP', 'ZP'],
            'iso_3166-2': ['02', '04', '08', '10', '06', '12', '14', '16', '20', '18', '22', '26', '24', '28', '30', '32']
            }
    return pd.DataFrame(data)


def get_poland_data():
    try:
        df_total = pd.read_html(URL_POLAND, header=0)[9]
        logger.info('Download total {data} frame from {url}'.format(url=URL_POLAND, data='df_total'))
        df_cases = pd.read_html(URL_POLAND, header=0)[10]
        logger.info('Download total {data} frame from {url}'.format(url=URL_POLAND, data='df_cases'))
        df_deaths = pd.read_html(URL_POLAND, header=0)[11]
        logger.info('Download total {data} frame from {url}'.format(url=URL_POLAND, data='df_deaths'))

        # Clean column names for total df
        df_total_columns = {name: name.split('[')[0].split('(')[0] for name in df_total.columns}
        df_total.rename(columns=df_total_columns, inplace=True)

        # Clean column names for cases df
        df_cases = switch_header_row(df_cases)
        df_cases = clean_header_voivodeship(df_cases)

        # Clean column names for deaths df
        df_deaths = switch_header_row(df_deaths)
        df_deaths = clean_header_voivodeship(df_deaths)

        # Remove trash records
        df_cases = df_cases[df_cases['Date'] != 'Infections per voivodeship']
        df_cases = df_cases[df_cases['Date'] != 'Date (CET)']
        df_cases = df_cases[~df_cases['Date'].str.contains('Notes')]

        df_deaths = df_deaths[df_deaths['Date'] != 'Deaths per voivodeship']
        df_deaths = df_deaths[df_deaths['Date'] != 'Date (CET)']
        df_deaths = df_deaths[~df_deaths['Date'].str.contains('Notes')]

        # Reshape cases and deaths df
        df_cases = pd.melt(df_cases,
                           id_vars=['Date'],
                           value_vars=['DS', 'KP', 'LB', 'LD', 'LU', 'MA', 'MZ', 'OP', 'PD', 'PK', 'PM','SK', 'SL', 'WN',
                                       'WP', 'ZP', 'daily', 'total'],
                           var_name ='iso_3166-1',
                           value_name ='Count')

        df_deaths = pd.melt(df_deaths,
                           id_vars=['Date'],
                           value_vars=['DS', 'KP', 'LB', 'LD', 'LU', 'MA', 'MZ', 'OP', 'PD', 'PK', 'PM', 'SK', 'SL', 'WN',
                                       'WP', 'ZP', 'daily', 'total'],
                           var_name='iso_3166-1',
                           value_name='Count')

        # Enrich data frames with voivodeship name and code and clean values
        df_voivodeship = get_poland_voivodeship_iso()
        df_cases = df_cases.merge(df_voivodeship, how='left', on='iso_3166-1')
        df_deaths = df_deaths.merge(df_voivodeship, how='left', on='iso_3166-1')

        df_cases['Date'] = df_cases['Date'].map(lambda x: x.split('[')[0])
        df_cases['Date'] = df_cases['Date'].map(lambda x: datetime.strptime(x, '%d %B %Y').strftime('%Y-%m-%d'))

        df_deaths['Date'] = df_deaths['Date'].map(lambda x: x.split('[')[0])
        df_deaths['Date'] = df_deaths['Date'].map(lambda x: datetime.strptime(x, '%d %B %Y').strftime('%Y-%m-%d'))

        df_cases['Count'] = df_cases['Count'].fillna(0)
        df_cases['Count'] = df_cases['Count'].map(lambda x: int(str(x).replace(' ', '').split('[')[0]))

        df_deaths['Count'] = df_deaths['Count'].fillna(0)
        df_deaths['Count'] = df_deaths['Count'].map(lambda x: int(str(x).replace(' ', '').split('[')[0]))

        df_poland_merged = df_cases.merge(df_deaths, how='left', on=['Date','iso_3166-1'])
        df_poland_merged = df_poland_merged[['Date', 'iso_3166-1', 'iso_3166-2_x', 'Voivodeship_x', 'Count_x', 'Count_y']]
        df_poland_merged.rename(columns={'Date': 'date',
                                         'iso_3166-2_x': 'iso_3166-2',
                                         'Voivodeship_x': 'voivodeship',
                                         'Count_x': 'cases',
                                         'Count_y':'deaths'}, inplace=True)
        df_poland_merged['deaths'] = df_poland_merged['deaths'].fillna(0)
        df_poland_merged['deaths'] = df_poland_merged['deaths'].astype('int')

        df_poland_merged.to_csv(FILE_PATH_POLAND, encoding='utf-8', sep='\t', index=False)
        logger.info('Successful saved data from {url}'.format(url=URL_POLAND))
    except Exception as e:
        logger.exception(e)
    return 0


def merge_data():
    df_country = get_country_data()
    df_covid = get_covid_data()
    df_country['country'] = df_country['names'].map(lambda x: country_intesection(FILE_PATH_CORONAVIRUS, FILE_PATH_COUNTRIES))
    df_country['country'] = [(set(a).intersection(b)) for a, b in zip(df_country.names, df_country.country)]
    df_country['country'] = df_country['country'].map(lambda x: list(map(str.casefold, x)))
    df_country['country'] = df_country['country'].map(lambda x: x[0] if len(x) > 0 else None)
    df = df_covid.merge(df_country, how='left', on='country')
    df['cases_population_percent'] = df['cases'] / df['population'] * 100
    df['cases_population_percent'] = df['cases_population_percent'].map(lambda x: format(x, '.4f'))
    df = df.set_index('date')

    df.to_csv(FILE_PATH_WORLD, encoding='utf8', sep='\t')

    return 0


if __name__=='__main__':
    logger.info('Run extractor')
    get_poland_data()
    merge_data()
    logger.info('End extractor')