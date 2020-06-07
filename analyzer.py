import pandas as pd
import ast


def get_countries(df):
    """return unique country list"""
    return sorted(list(df.country.unique()),key=str)


def get_regions(df):
    """return unique region list"""
    return sorted(list(df.region.unique()),key=str)


def get_voivodeship(df):
    """return unique region list"""
    return sorted(list(df.voivodeship.unique()),key=str)


def get_max_date(df):
    """return last date of data"""
    return max(df.date)


def get_dates(df):
    """return list of data dates"""
    return list(df.date.unique())


def get_last_data(df):
    """Some documentation of function"""
    return df.loc[df['date']==max(get_dates(df))].sort_values(by='cases', ascending=False)


def country_substract(df_covid, df_country):
    """Some documentation of function"""
    return set(df_covid.country).difference(set([str(country).casefold() for sublist in df_country.names.tolist() for country in ast.literal_eval(sublist)]))


def country_intesection(path_covid, path_country):
    """Some documentation of function"""
    df_covid = pd.read_csv(path_covid, sep='\t', encoding='utf-8')
    df_country = pd.read_csv(path_country, sep='\t', encoding='utf-8')
    return sorted(list(set(df_covid.country).intersection(set([str(country).casefold() for sublist in df_country.names.tolist() for country in ast.literal_eval(sublist)]))))


def init_df(path):
    return pd.read_csv(path, sep='\t', encoding='utf-8')

