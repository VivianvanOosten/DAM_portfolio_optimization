import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import gurobipy as gp
from gurobipy import GRB,quicksum
from dash import Dash, dcc, html, Input, State, Output, callback, no_update
from dash.exceptions import PreventUpdate
from fct_optimizer import covariance, returns, assets, creating_and_running_optimizer

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

monthly_or_not = html.Div(
    [
        dbc.Label("Is the amount below a monthly or a one-off investment?"),
        dbc.RadioItems(
            id="monthly_or_not",
            options=[{"label": 'Monthly', "value": 1}, {'label': "One-off", 'value': 0}],
            value= risk_choices[0],
            inline=True,
        ),
    ],
    className="mb-4",
)

amount_invested_input = dbc.Row(
    [
    dbc.Label("Set investment amount"),
    dbc.Col(
        dbc.Input(id = 'amount_invested',
                  type="number", #min=0, max=10000, step=1,
                  placeholder = 'Write the investment amount here: 0 - 10 thousand'),
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
                  type="number", #min=0, max=10**7, step=1,
                  placeholder = 'Write the investment goal here: 0 - 10 million'
                  ),
        width = 10
    )
    # , # Leaving out the currency for now - too complex
    # dbc.Col(
    # currency_dropdown,
    # width = 2
    # )
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
     monthly_or_not, 
     amount_invested_input, 
     amount_goal_input, 
     submit
     ]
)


# # OUTPUTS
df = pd.DataFrame({
    "Assets": assets,
    "Amount": [0]*len(assets)
})

fig = px.pie(df, values="Amount", names = 'Assets')



outputs = html.Div(
    [html.Div(id = 'showing_text', children = 'our output is this'),
     dcc.Graph(
        id='pie_chart',
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
    'Moderate'      : 100,
    'Conservative'  : 0.03
}

@callback(
    Output("showing_text", 'children'),
    Output('pie_chart', 'figure'),
    Input('submit-val', 'n_clicks'),
    State('risk_level', 'value'),
    State('years', 'value'),
    State('amount_invested','value'),
    State('goal_amount','value'),
    State('monthly_or_not','value')
)
def update_output(submission_number, risk, years, amount_invested, min_return, installment_flag):

    if installment_flag == 1:
        amount_invested = amount_invested * 12 * years
        print(amount_invested)

    if submission_number is None or submission_number == 0:
        return "No data yet", no_update
    
    max_risk = risk_dict[risk]

    m, investment_amount = creating_and_running_optimizer(years, min_return, max_risk, amount_invested, covariance, returns, assets, installment_flag)

    if m.status == GRB.OPTIMAL:
        print('\nPortfolio Return: %g' % m.objVal)
        print('\nInvestment Amount:')
        investment_amountx = m.getAttr('x', investment_amount) 
        for a in assets:            
                print('%s %g' % (a, investment_amountx[a]))
    else:
        print('No solution:', m.status)
        text = html.H1(
            [
                html.Div("No solution with these inputs", style={"color": "red"}),
            ]
        )
        return text, px.pie()

    
    text = ['We have chosen risk level: {}'.format(risk),
            html.Br(), 
            'outcome of optimizer is {}'.format(m.objVal)
            ]
    

    df = pd.DataFrame({
        'Assets': investment_amountx.keys(), 
        'Amount': investment_amountx.values(), 
        })

    fig = px.pie(df, values="Amount", names = 'Assets')


    
    return text, fig





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


# NOTE: color-code assets by risk-level