import pandas as pd
from os import path

FILE_PATH = path.abspath(path.join(path.join(path.dirname(__file__),'data','coronavirus.tsv')))
FILE_PATH_COUNTRIES = path.abspath(path.join(path.join(path.dirname(__file__),'data','countries.tsv')))
df = pd.read_csv(FILE_PATH, sep='\t', encoding='utf-8')
df_c = pd.read_csv(FILE_PATH_COUNTRIES, sep='\t', encoding='utf-8')

def get_countries(df):
    return sorted(list(df.country.unique()),key=str)

def get_dates(df):
    return list(df.date.unique())

def get_last_data(df):
    return df.loc[df['date']==max(get_dates(df))].sort_values(by='cases', ascending=False)

def country_substract(df_covid=df, df_country=df_c):
    return set(df_covid.country).difference(set([country.strip() for sublist in df_country.names.tolist() for country in
                                            sublist.replace('[', '').replace(']', '').replace('\'','').split(',')]))

def country_intesection(df_covid=df, df_country=df_c):
    return list(set(df_covid.country).intersection(set([country.strip() for sublist in df_country.names.tolist() for country in
                                          sublist.replace('[', '').replace(']', '').replace('\'', '').split(',')])))

if __name__=='__main__':
    print(country_substract())