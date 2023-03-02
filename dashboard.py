import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, State, Output, callback

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc_css])


# styling
theme_colors = [
    "primary",
    "secondary",
    "success",
    "warning",
    "danger",
    "info",
    "light",
    "dark",
    "link",
]


# variables
risk_choices = ['Moderate','Conservative']

header = html.H4(
    "Portfolio optimization for LBS students", className="bg-primary text-white p-2 mb-2 text-center"
)

checklist = html.Div(
    [
        dbc.Label("Select Risk Level"),
        dbc.RadioItems(
            id="risk_level",
            options=[{"label": i, "value": i} for i in risk_choices],
            value= risk_choices[0],
            inline=True,
        ),
    ],
    className="mb-4",
)

years = range(0,80)
slider = html.Div(
    [
        dbc.Label("Select Time-horizon"),
        dcc.RangeSlider(
    

            years[0],
            years[-1],
            5,
            id="years",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            value=[years[0], years[-5]],
            className="p-0",
        ),
    ],
    className="mb-4",
)

submit = html.Button('Submit', id='submit-val', n_clicks=0)

controls = dbc.Card(
    [checklist,slider, submit],
    body=True,
)



# # OUTPUTS
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.pie(df, values="Amount", names = 'Fruit')



outputs = dbc.Card(
    [html.Div(id = 'showing_text', children = 'our output is this'),
     dcc.Graph(
        id='example-graph',
        figure=fig
    )],
    body=True
)



# # APP LAYOUT GENERAL

app.layout = html.Div(children=[
    dbc.Container([
    header,
    dbc.Row([
        dbc.Col(
            controls
            ),
            
        dbc.Col(
            outputs
        )],
        justify='center'
        )
    ])
])


@callback(
    Output("showing_text", 'children'),
    Input('submit-val', 'n_clicks'),
    State('risk_level', 'value'),
    State('years', 'value')
)
def update_line_chart(submission_number, risk, years):
    
    text = ['We have chosen risk level: {}'.format(risk),
            html.Br(), 
            'and a time-frame between {} and {}'.format(years[0], years[1])]

    return text


# actually running the app
if __name__ == '__main__':
    app.run_server(debug=True)



"""
NOTE ON DEPLOYMENT
use: https://towardsdatascience.com/the-easiest-way-to-deploy-your-dash-app-for-free-f92c575bb69e

LEFTOVER CODE
    
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

, 
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )

"""