import pandas as pd
from extractor import FILE_PATH, FILE_PATH_COUNTRIES

df = pd.read_csv(FILE_PATH, sep='\t', encoding='utf-8')
#df = df.loc[df['country'].isin(['poland', 'germany', 'italy', 'czech republic'])]
df_c = pd.read_csv(FILE_PATH_COUNTRIES, sep='\t', encoding='utf-8')

def get_countries(df):
    return sorted(list(df.country.unique()),key=str)

def get_dates(df):
    return list(df.date.unique())

def get_last_data(df):
    return df.loc[df['date']==max(get_dates(df))].sort_values(by='cases', ascending=False)

def country_substract(df_covid, df_country):
    return set(df_covid.country).difference(set([country.strip() for sublist in df_country.names.tolist() for country in sublist.replace('[', '').replace(']', '').replace('\'','').split(',')]))


if __name__=='__main__':
    pass