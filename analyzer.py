import pandas as pd
import ast
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
    """return unique country list"""
    return sorted(list(df.country.unique()),key=str)

def get_regions(df):
    """return unique region list"""
    return sorted(list(df.region.unique()),key=str)

def get_max_date(df):
    """return last date of data"""
    return max(df.date)

def get_dates(df):
    """return list of data dates"""
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

def init_df(path=FILE_PATH_MERGED):
    return pd.read_csv(path, sep='\t', encoding='utf-8')

if __name__=='__main__':
    df = init_df()
    grouped_df = df.groupby(['date', 'region'], as_index=False).agg({'cases': 'sum', 'deaths': 'sum', 'new_cases': 'sum'})
    print(grouped_df.head(100))