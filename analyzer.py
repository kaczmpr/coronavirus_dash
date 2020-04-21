import pandas as pd
import ast
import plotly.express as px
import plotly.graph_objects as go
from os import path
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

FILE_PATH = path.abspath(path.join(path.join(path.dirname(__file__),'data','coronavirus.tsv')))
FILE_PATH_COUNTRIES = path.abspath(path.join(path.join(path.dirname(__file__),'data','countries.tsv')))
FILE_PATH_MERGED = path.abspath(path.join(path.join(path.dirname(__file__),'data','merged.tsv')))
df = pd.read_csv(FILE_PATH, sep='\t', encoding='utf-8')
df_c = pd.read_csv(FILE_PATH_COUNTRIES, sep='\t', encoding='utf-8')
df_m = pd.read_csv(FILE_PATH_MERGED, sep='\t', encoding='utf-8')

def get_countries(df):
    """Some documentation of function"""
    return sorted(list(df.country.unique()),key=str)

def get_dates(df):
    """Some documentation of function"""
    return list(df.date.unique())

def get_last_data(df):
    """Some documentation of function"""
    return df.loc[df['date']==max(get_dates(df))].sort_values(by='cases', ascending=False)

def country_substract(df_covid=df, df_country=df_c):
    """Some documentation of function"""
    return set(df_covid.country).difference(set([str(country).casefold() for sublist in df_country.names.tolist() for country in ast.literal_eval(sublist)]))

def country_intesection(df_covid=df, df_country=df_c):
    """Some documentation of function"""
    return sorted(list(set(df_covid.country).intersection(set([str(country).casefold() for sublist in df_country.names.tolist() for country in ast.literal_eval(sublist)]))))

def get_map_data(df=df_m):
    df = df_m[['date', 'country', 'cases', 'day_of_epidemie', 'new_cases', 'name', 'alpha3Code', 'region']]
    df.dropna(inplace=True)
    return df

if __name__=='__main__':
    get_map_data()
