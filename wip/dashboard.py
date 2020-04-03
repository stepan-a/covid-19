# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import covid19

PORT = "8000"
ADDRESS = "127.0.0.2"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data_confirmed, data_deaths, countries = covid19.data_import()

fig = covid19.chart(countries=countries,
      data = data_confirmed,
      data_rolling = data_confirmed,
      by_million_inh = False,
      last_d = int(len(data_confirmed)/2),
      name_fig = ""
     )


app.layout = html.Div(children=[
    html.H1(children='Coronavirus Covid-19 Dashboard'),

    html.Div(id="a",
    children='''
        Data: CSSE. Author: @guillaumerozier.
    '''),

    html.Div(
        children=[
        html.H6(''),
        html.Div(
            children=[
            #html.H6('Confirmed cases or deaths'),
            dcc.RadioItems(
                id="cases",
                options=[
                    {'label': 'Confirmed cases', 'value': 'cases'},
                    {'label': 'Deaths', 'value': 'deaths'}
                ],
                value='cases'
            )],
            style = {'position':'absolute', 'left':'20%'}
        ),
        html.Div(
            children=[
            #html.H6('By inhabitant'),
            dcc.Checklist(
            id="million",
            options=[
                {'label': 'By million inhabitants', 'value': 'million'}
                    ]
                )],
            style = {'position':'absolute', 'left':'60%'}
            )],
            style = {'width':'40%', 'height':'80px','position':'absolute', 'left':'25%', 'margin-top':'20px', 'border':'1px', 'border-style': 'solid'}
        ),

        html.Div(
            children=[
            html.H6('Number of days to show'),
            dcc.Slider(
            id="days",
            min=10,
            max=40,
            step=2,
            marks={i: '{}'.format(i) for i in range(50)},
            value=20
            )],
            style={'width':'50%', 'position':'absolute', 'left':'25%', 'margin-top':'650px'}
        ),


    html.Div(
    children=[
    html.Div(children=[
        dcc.Graph(
            id='chart1',
            figure=fig
        )
        ], style={'width':'60%', 'height':'90%', 'margin': 'auto', 'max-width':'1300px', 'min-height': '200px', 'min-width': '600px'}
    )],
    style={'margin-top':'200px'}),



])


@app.callback(
    Output(component_id='chart1', component_property='figure'),
    [Input(component_id='cases', component_property='value'),
    Input(component_id='million', component_property='value'),
    Input(component_id='days', component_property='value')]
)
def update_output_div(cases_deaths, million, last_d):

    by_million = False
    if cases_deaths == "cases":
        ppl = "cases"
        data = data_confirmed
    else:
        ppl = "deaths",
        data = data_deaths

    if million:
        by_million = True
    print(million)
    print(cases_deaths)

    return covid19.chart(countries = countries,
          data = data,
          data_rolling = data,
          by_million_inh = by_million,
          last_d = last_d,
          name_fig = "",
          type_ppl = ppl,
         )


if __name__ == '__main__':
    app.run_server(debug=True, port=PORT)
