import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import gurobipy as gp
from gurobipy import GRB,quicksum
from dash import Dash, dcc, html, Input, State, Output, callback, no_update
from dash.exceptions import PreventUpdate
from fct_optimizer import covariance, returns, creating_and_running_optimizer

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc_css])


# variables
risk_choices = ['Moderate','Conservative']

header = html.H4(
    "Portfolio optimization for LBS students", className="bg-primary text-white p-2 mb-2 text-center"
)

risk_level_checklist = html.Div(
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

currencies = ['$','€','£']
currency_dropdown = dcc.Dropdown(
    id="Currency",
    options = [{"label": i, "value": i} for i in currencies],
    style = {'color': '#000000'},
)

amount_invested_input = dbc.Row(
    [
    dbc.Label("Set monthly investment"),
    dbc.Col(
        dbc.Input(id = 'amount_invested',
                  type="number", min=0, max=10000, step=1,
                  placeholder = 'Write the monthly investment amount here: 0 - 10 thousand'),
        width = 10
    )
    ],
    className="mb-4",
)

amount_goal_input = dbc.Row(
    [
    dbc.Label("Set goal amount after time period"),
    dbc.Col(
        dbc.Input(id = 'goal_amount',
                  type="number", min=0, max=10**7, step=1,
                  placeholder = 'Write the investment goal here: 0 - 10 million'
                  ),
        width = 10
    ),
    dbc.Col(
    currency_dropdown,
    width = 2
    )
    ],
    className="mb-4",
)


years = range(0,80)
slider = html.Div(
    [   dbc.Label("Select Time-horizon"),
        dcc.Slider(
            years[0],
            years[-1],
            5,
            id="years",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            value= years[-5],
            className="p-0",
        ),
    ],
    className="mb-4",
)

submit = html.Button('Submit', id='submit-val', n_clicks=0)

controls = html.Div(
    [risk_level_checklist, 
     slider, 
     amount_invested_input, 
     amount_goal_input, 
     submit
     ]
)


# # OUTPUTS
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.pie(df, values="Amount", names = 'Fruit')



outputs = html.Div(
    [html.Div(id = 'showing_text', children = 'our output is this'),
     dcc.Graph(
        id='example-graph',
        figure=fig
    )]
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


risk_dict = {
    'Moderate'      : 0.1,
    'Conservative'  : 0.03
}

@callback(
    Output("showing_text", 'children'),
    Input('submit-val', 'n_clicks'),
    State('risk_level', 'value'),
    State('years', 'value'),
    State('amount_invested','value'),
    State('goal_amount','value')
)
def update_output(submission_number, risk, years, amount_invested, min_return):

    if submission_number is None or submission_number == 0:
         return no_update
    

    max_risk = risk_dict[risk]

    m = creating_and_running_optimizer(years, min_return, max_risk, amount_invested, covariance, returns)
    m.optimize()
    
    text = ['We have chosen risk level: {}'.format(risk),
            html.Br(), 
            'outcome of optimizer is {}'.format(m.objVal)
            ]
    
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