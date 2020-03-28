import pandas as pd
from extractor import FILE_PATH

df = pd.read_csv(FILE_PATH, sep='\t', encoding='utf-8')
df = df.loc[df['country'].isin(['poland', 'germany', 'italy', 'czech republic'])]

def get_countries(df):
    return sorted(list(df.country.unique()))

def get_dates(df):
    return list(df.date.unique())

def get_last_data(df):
    return df.loc[df['date']==max(get_dates(df))].sort_values(by='cases', ascending=False)

if __name__=='__main__':
    pass