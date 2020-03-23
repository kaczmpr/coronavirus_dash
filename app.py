import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import analyzer
import plotly.graph_objects as go
from extractor import FILE_PATH

# Read data from datafile
df = pd.read_csv(FILE_PATH, sep='\t')
df = df.loc[df['country'].isin(['poland', 'germany', 'italy', 'czech republic'])]
COUNTRIES = analyzer.get_countries(df)
DATES = analyzer.get_dates(df)

def generate_table(df, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))

        ])
    ])

def generate_scatter_ploat(df):
    return dcc.Graph(
        id='scatter_plot_country',
        figure={
            'data': [
                dict(
                    x=df[df['country']==i]['day_of_epidemie'],
                    y=df[df['country']==i]['cases'],
                    text=df[df['country']==i]['country'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in COUNTRIES
            ],
            'layout': dict(
                xaxis={'type': 'log', 'title': 'Day of epidemie'},
                yaxis={'title': 'Number of cases'},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )

def generate_bar_plot(df):
    return dcc.Graph(
        id='bar_plot',
        figure={
            'data': [
                {'x': list(df.loc[df['country']=='poland'].date), 'y': list(df.loc[df['country']=='poland'].cases), 'type': 'bar', 'name': 'Poland'},
            ],
            'layout': {
                'title': 'Number of COVID-19 cases in country'
            }
        }
    )

def select_country():
    return dcc.Dropdown(
        options=[
            dict(
                label=country.capitalize(),
                value=country)
        for country in COUNTRIES
        ],
        value=COUNTRIES[0].capitalize()
    )

def select_slider(df):
    return dcc.Slider(
        min=min(df.day_of_epidemie),
        max=max(df.day_of_epidemie),
        marks={day: 'Day {daye}'.format(daye=day) for day in range(min(df.day_of_epidemie), max(df.day_of_epidemie))},
        value=20
    )

# Init application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Set colors
colors = {
    'background': '#303030',
    'text_h1': '#ffffff'
}

# Set layout
app.layout = html.Div(children=[
    html.H1(children='Coronavirus dashboard',
            style={
                'textAlign': 'center',
            }),
    html.Div(children=[
        select_country(),
        generate_bar_plot(df),
        html.H4(children='Country cases'),
        generate_table(analyzer.get_last_data(df)),
        generate_scatter_ploat(analyzer.get_last_data(df)),
        select_slider(analyzer.get_last_data(df))
    ]),
])

if __name__=='__main__':
    app.run_server(debug=True)