import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import analyzer
import plotly.graph_objects as go
from extractor import FILE_PATH, FILE_PATH_MERGED
from dash.dependencies import  Input, Output


# Read data from datafile
df = pd.read_csv(FILE_PATH_MERGED, sep='\t', encoding='utf-8')

COUNTRIES = analyzer.get_countries(df)
DATES = analyzer.get_dates(df)

def select_country():
    return dcc.Dropdown(
        id='select_dropdown_country',
        options=[
            dict(
                label=str(country).capitalize(),
                value=str(country))
            for country in COUNTRIES
        ],
        value=['poland'],
        multi=True
    )

def select_slider(df):
    return dcc.Slider(
        id='select_slider_days',
        min=min(df.day_of_epidemie),
        max=max(df.day_of_epidemie),
        marks={day: 'Day {daye}'.format(daye=day) for day in range(min(df.day_of_epidemie), max(df.day_of_epidemie))},
        value=20
    )

def select_checkbox():
    return dcc.Dropdown(
        id='select_checkbox_type_value',
        options=[
            {'label': 'cases', 'value': 'cases'},
            {'label': 'deaths', 'value': 'deaths'},
        ],
        value='cases'
    )


def select_range_slider():
    return dcc.RangeSlider(
        id='select_rangeslider_days',
        marks={day: '{}'.format(day) for day in range(min(df.day_of_epidemie), max(df.day_of_epidemie))},
        min = min(df.day_of_epidemie),
        max = max(df.day_of_epidemie),
        value=[min(df.day_of_epidemie), min(df.day_of_epidemie)+10]
    )


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

def generate_line_plot(df):
    return dcc.Graph(
        id='line_plot_country',
        figure={
            'data': [
                dict(
                    x=list(df.loc[df['country'] == country].date),
                    y=list(df.loc[df['country'] == country].cases),
                    type='line',
                    name=country
                )
            for country in COUNTRIES
            ],
            'layout': dict(
                title='Number of COVID-19 cases in country'
            )
        }
    )


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
                'textAlign': 'center'
            }),
    html.Div(children=[
        select_country(),
    ], style={'width': '48%', 'display': 'inline-block'}
    ),
    html.Div(children=[
        select_checkbox(),
    ], style={'width': '48%', 'display': 'inline-block'}
    ),
    html.Div(children=[
        select_range_slider(),
    ]
    ),
    html.Div(children=[
        dcc.Graph(id='line_plot_country')
    ])
])

@app.callback(
    Output('line_plot_country','figure'),
    [Input('select_dropdown_country', 'value'),
     Input('select_rangeslider_days', 'value'),
     Input('select_checkbox_type_value', 'value')]
)
def update_line_plot(selected_countries, selected_days, selected_type):
    filtered_df = df[df['country'].isin(selected_countries) & df['day_of_epidemie'].isin(range(selected_days[0], selected_days[1]))]
    traces = []
    for country in filtered_df.country.unique():
        df_by_country = filtered_df[filtered_df['country'] == country]
        traces.append(dict(
            x=df_by_country['day_of_epidemie'],
            y=df_by_country[selected_type],
            mode='lines+markers',
            text=country,
            textposition='bottom center',
            type='scatter',
            name=country
        ))
    return {
        'data': traces,
        'layout': dict(
            title='Number of COVID-19 cases in country',
            showlegend=True,
            xaxis=dict(title='Days of epidemie'),
            yaxis=dict(title='Count'),
        )
    }

if __name__=='__main__':
    app.run_server(debug=True)