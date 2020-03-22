import dash
import dash_core_components as dcc
import dash_html_components as html
from extractor import FILE_PATH
import pandas as pd

# Read data from datafile
df = pd.read_csv(FILE_PATH, sep='\t')
COUNTRIES = list(df.country.unique())
DATES = list(df.date.unique())

# Init application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Set colors
colors = {
    'background': '#303030',
    'text_h1': '#ffffff'
}

# Set layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Coronavirus dashboard',
            style={
                'textAlign': 'center',
                'color': colors['text_h1']
            }
    ),
    dcc.Graph(
        id='example_dag',
        figure={
            'data': [
                {'x': list(df.loc[df['country']=='Poland'].date), 'y': list(df.loc[df['country']=='Poland'].cases), 'type': 'bar', 'name': 'Poland'},
                {'x': list(df.loc[df['country']=='Germany'].date), 'y': list(df.loc[df['country']=='Germany'].cases), 'type': 'bar', 'name': 'Germany'},
            ],
            'layout': {
                'title': 'Number of COVID-19 cases in country',
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text_h1']
                }
            }
        }
    ),

    html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H3(children='Report Continuitty',
                style={
                    'textAlgin': 'center',
                    'color': colors['text_h1']
                }
                )
    ]),
])

if __name__=='__main__':
    app.run_server(debug=True)