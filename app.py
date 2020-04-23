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

# Create country tab
def build_country_inputs():
    return html.Div([
        html.Div([
            html.Div([
                html.P(),
                html.H5('Input parameters country'),
                dcc.Dropdown(
                    id='country_tab_country',
                    options=[
                        dict(
                            label=str(country).capitalize(),
                            value=str(country))
                        for country in analyzer.get_countries(df)
                    ],
                    placeholder='Select country',
                    value=['poland','sweden','czech republic'],
                    multi=True,
                    style={'padding': '10px', 'max-width': '800px'}
                )
            ], className='six columns'),

            html.Div([
                html.P(),
                html.H5('Input parameters type'),
                dcc.RadioItems(
                    id='country_tab_type',
                    options=[
                        {'label': 'cases', 'value': 'cases'},
                        {'label': 'deaths', 'value': 'deaths'},
                    ],
                    value='cases',
                )
            ], className='six columns'),
        ], className='row'),

        html.Div([
            html.Div([
                html.P(),
                html.H5('Input parameters type'),
                dcc.RangeSlider(
                    id='country_tab_days',
                    marks={day: '{}'.format(day) for day in range(1, max(df.day_of_epidemie))},
                    min=1,
                    max=max(df.day_of_epidemie),
                    value=[1, 50]
                )
            ]),
        ], className='row')
    ])


def build_continet_tab():
    return html.Div([
        html.Div([
            html.Div([
                html.P(),
                html.H5('Input parameters region'),
                dcc.Dropdown(
                    id='region_tab_region',
                    options=[
                        dict(
                            label=str(region).capitalize(),
                            value=str(region))
                        for region in analyzer.get_regions(df)
                    ],
                    placeholder='Select region',
                    value=['Asia', 'Americas', 'Europe'],
                    multi=True,
                    style={'padding': '10px', 'max-width': '800px'}
                )
            ], className='six columns'),

            html.Div([
                html.P(),
                html.H5('Input parameters type'),
                dcc.RadioItems(
                    id='region_tab_type',
                    options=[
                        {'label': 'cases', 'value': 'cases'},
                        {'label': 'deaths', 'value': 'deaths'},
                    ],
                    value='cases',
                )
            ], className='six columns'),
        ], className='row'),
    ])


def build_poland_tab():
    pass


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
                        children=[
                            build_country_inputs(),
                            dcc.Graph(id='line_plot_country'),
                            dcc.Graph(id='line_plot_new_cases'),
                            dcc.Graph(id='line_plot_percent_of_new_cases'),
                            dcc.Graph(id='line_plot_percent_of_population'),
                        ]
                    ),
                    dcc.Tab(
                        id='continent_tab',
                        label='Continent',
                        value='tab2',
                        className='custom_tab',
                        selected_className='custom_tab_selected',
                        children=[
                            build_continet_tab(),
                            dcc.Graph(id='line_plot_continent'),
                            dcc.Graph(id='region_pie_chart'),
                        ]
                    ),
                    dcc.Tab(
                        id='poland_tab',
                        label='Poland',
                        value='tab3',
                        className='custom_tab',
                        selected_className='custom_tab_selected',
                        children=[
                            html.H3('Poland')
                        ]
                    ),
                ],
            )
        ],
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

app.config["suppress_callback_exceptions"] = True

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
    ]
)


@app.callback(
    Output('line_plot_country','figure'),
    [Input('country_tab_country', 'value'),
     Input('country_tab_days', 'value'),
     Input('country_tab_type', 'value')]
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
    [Input('country_tab_country', 'value'),
     Input('country_tab_days', 'value'),
     Input('country_tab_type', 'value')]
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
    [Input('country_tab_country', 'value'),
     Input('country_tab_days', 'value'),
     Input('country_tab_type', 'value')]
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
    [Input('country_tab_country', 'value'),
     Input('country_tab_days', 'value'),
     Input('country_tab_type', 'value')]
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


@app.callback(
    Output('line_plot_continent', 'figure'),
    [Input('region_tab_region', 'value'),
     Input('region_tab_type', 'value')]
)
def update_line_plot_continent(selected_region, selected_type):
    grouped_df = df.groupby(['date', 'region'], as_index=False).agg({'cases': 'sum', 'deaths': 'sum', 'new_cases': 'sum'})
    filtered_df = grouped_df[grouped_df['region'].isin(selected_region)]
    traces = []
    for region in filtered_df.region.unique():
        df_by_region = filtered_df[filtered_df['region'] == region]
        traces.append(dict(
            x=df_by_region['date'],
            y=df_by_region[selected_type],
            mode='lines+markers',
            text=region,
            textposition='bottom center',
            type='scatter',
            name=region
        ))
    return {
        'data': traces,
        'layout': dict(
            title='Daily COVID-19 cases in region',
            showlegend=True,
            xaxis=dict(title='Date'),
            yaxis=dict(title='Count'),
        )
    }


@app.callback(
    Output('region_pie_chart', 'figure'),
    [Input('region_tab_region', 'value'),
     Input('region_tab_type', 'value')],
)
def update_region_pie_char(selected_region, selected_type):
    grouped_df = df.groupby(['date', 'region'], as_index=False).agg({'cases': 'sum', 'deaths': 'sum', 'new_cases': 'sum'})
    filtered_df = grouped_df[grouped_df['date'] == analyzer.get_max_date(df)]
    return {
        'data': [go.Pie(labels=filtered_df.region, values=filtered_df[selected_type])],
        'layout': go.Layout(title='Pie chart')
    }


if __name__=='__main__':
    app.run_server(debug=True)