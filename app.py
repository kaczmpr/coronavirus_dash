import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import analyzer
import plotly.graph_objects as go
import plotly.express as px
from extractor import FILE_PATH_MERGED
from dash.dependencies import  Input, Output

# Read data from datafile
df = pd.read_csv(FILE_PATH_MERGED, sep='\t', encoding='utf-8')

COUNTRIES = analyzer.get_countries(df)
DATES = analyzer.get_dates(df)


def build_title():
    return html.Div(
        id='title',
        className='title',
        children=[
            html.Div(
                id='title_text',
                children=[
                    html.H5('Coronavirus pandemic spread dashboard'),
                    html.H6('Disease control and country analysis tool')
                ],
            ),
            html.Div(
                id='title_logo',
                children=[
                    html.Button(
                        id='learn_more_button', children='LEARN MORE', n_clicks=0
                    ),
                ],
            ),
        ],
    )


def build_tabs():
    return html.Div(
        id='tabs',
        className='tabs',
        children=[
            dcc.Tabs(
                id='app_tabs',
                value='tab1',
                className='custom_tabs',
                children=[
                    dcc.Tab(
                        id='country_tab',
                        label='Country',
                        value='tab1',
                        className='custom_tab',
                        selected_className='custom_tab_selected',
                    ),
                    dcc.Tab(
                        id='continent_tab',
                        label='Continent',
                        value='tab2',
                        className='custom_tab',
                        selected_className='custom_tab_selected'
                    ),
                    dcc.Tab(
                        id='poland_tab',
                        label='Poland',
                        value='tab3',
                        className='custom_tab',
                        selected_className='custom_tab_selected'
                    ),
                ],
            )
        ],
    )

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

def dropdown_contry():
    return (
        dcc.Dropdown(
            id='dropdown_country'
        )
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


def select_range_slider(name='select_rangeslider_days'):
    return dcc.RangeSlider(
        id=name,
        marks={day: '{}'.format(day) for day in range(min(df.day_of_epidemie), max(df.day_of_epidemie))},
        min = min(df.day_of_epidemie),
        max = max(df.day_of_epidemie),
        value=[min(df.day_of_epidemie), min(df.day_of_epidemie)+10]
    )


def generate_map_cases_plot(df):
    df = df[['date', 'country', 'cases', 'day_of_epidemie', 'new_cases', 'name', 'alpha3Code', 'region']]
    df.dropna(inplace=True)
    fig = px.scatter_geo(df, locations='alpha3Code', size='cases', hover_name='name', animation_frame='day_of_epidemie', color='region')
    fig.update_geos(showcountries=True)
    return fig.show()

# Init application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# Set colors
colors = {
    'background': '#303030',
    'text_h1': '#ffffff'
}


# Set layout
app.layout = html.Div(
    id='big_app_container',
    children=[
        build_title(),
        html.Div(
            id='app_container',
            children=[
                build_tabs(),
                html.Div(id='app_content')
            ]
        )
        #html.Div(children=[
        #    select_country(),
        #], style={'width': '48%', 'display': 'inline-block'}
        #),
        #html.Div(children=[
        #    select_checkbox(),
        #], style={'width': '48%', 'display': 'inline-block'}
        #),
        #html.Div(children=[
        #    select_range_slider(),
        #]
        #),
        #html.Div(children=[
        #    dcc.Graph(id='line_plot_country')
        #]
        #),
        #html.Div(children=[
        #    dcc.Graph(id='line_plot_new_cases')
        #]),
        #html.Div(children=[
        #    dcc.Graph(id='line_plot_percent_of_new_cases')
        #]),
        #html.Div(children=[
        #    dcc.Graph(id='line_plot_percent_of_population')
    ]
)
#])

@app.callback(
    [Output('app_content','children')],
    [Input('app_tabs','value')],
)
def update_select_country(tab_switch):
    if tab_switch == 'tab1':
        return html.Div(
            children=[
                select_country(),
            ],
        )


"""
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

@app.callback(
    Output('line_plot_new_cases','figure'),
    [Input('select_dropdown_country', 'value'),
     Input('select_rangeslider_days', 'value'),
     Input('select_checkbox_type_value', 'value')]
)
def update_line_plot_new_cases(selected_countries, selected_days, selected_type):
    filtered_df = df[df['country'].isin(selected_countries) & df['day_of_epidemie'].isin(range(selected_days[0], selected_days[1]))]
    traces = []
    for country in filtered_df.country.unique():
        df_by_country = filtered_df[filtered_df['country'] == country]
        traces.append(dict(
            x=df_by_country['day_of_epidemie'],
            y=df_by_country['new_cases'],
            mode='lines+markers',
            text=country,
            textposition='bottom center',
            type='scatter',
            name=country
        ))
    return {
        'data': traces,
        'layout': dict(
            title='Daily growth of COVID-19 new cases',
            showlegend=True,
            xaxis=dict(title='Days of epidemie'),
            yaxis=dict(title='Count'),
        )
    }

@app.callback(
    Output('line_plot_percent_of_new_cases','figure'),
    [Input('select_dropdown_country', 'value'),
     Input('select_rangeslider_days', 'value'),
     Input('select_checkbox_type_value', 'value')]
)
def update_line_plot_percent_of_new_cases(selected_countries, selected_days, selected_type):
    filtered_df = df[df['country'].isin(selected_countries) & df['day_of_epidemie'].isin(range(selected_days[0], selected_days[1]))]
    traces = []
    for country in filtered_df.country.unique():
        df_by_country = filtered_df[filtered_df['country'] == country]
        traces.append(dict(
            x=df_by_country['day_of_epidemie'],
            y=df_by_country['new_cases_percent'],
            mode='lines+markers',
            text=country,
            textposition='bottom center',
            type='scatter',
            name=country
        ))
    return {
        'data': traces,
        'layout': dict(
            title='Daily percent growth of COVID-19 new cases',
            showlegend=True,
            xaxis=dict(title='Days of epidemie'),
            yaxis=dict(title='Count'),
        )
    }

@app.callback(
    Output('line_plot_percent_of_population','figure'),
    [Input('select_dropdown_country', 'value'),
     Input('select_rangeslider_days', 'value'),
     Input('select_checkbox_type_value', 'value')]
)
def update_line_plot_percent_of_population(selected_countries, selected_days, selected_type):
    filtered_df = df[df['country'].isin(selected_countries) & df['day_of_epidemie'].isin(range(selected_days[0], selected_days[1]))]
    traces = []
    for country in filtered_df.country.unique():
        df_by_country = filtered_df[filtered_df['country'] == country]
        traces.append(dict(
            x=df_by_country['day_of_epidemie'],
            y=df_by_country['cases_population_percent'],
            mode='lines+markers',
            text=country,
            textposition='bottom center',
            type='scatter',
            name=country
        ))
    return {
        'data': traces,
        'layout': dict(
            title='Daily percent COVID-19 cases in population',
            showlegend=True,
            xaxis=dict(title='Days of epidemie'),
            yaxis=dict(title='Count'),
        )
    }
"""

if __name__=='__main__':
    app.run_server(debug=True)