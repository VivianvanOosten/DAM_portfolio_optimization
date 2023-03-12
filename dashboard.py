import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import gurobipy as gp
from gurobipy import GRB,quicksum
from dash import Dash, dcc, html, Input, State, Output, callback, no_update
from dash.exceptions import PreventUpdate
from fct_optimizer import covariance, mean_returns, creating_and_running_optimizer

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc_css])


assets = ['riskfree', 'bitcoin', 'gold', 'ftse', 'house_prices', 'bank_rates'] 


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

min_nr_assets = dbc.Row(
    [
    dbc.Label("Set the minimum number of different assets"),
    dbc.Col(
        dbc.Input(id = 'min_assets',
                  type="number", min=0, max=7, step=1,
                  placeholder = 'Minimum number of different assets: 0 - 7'
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

submit = html.Button('Submit', id='submit-val', n_clicks=0)

controls = html.Div(
    [risk_level_checklist, 
     slider, 
     monthly_or_not, 
     amount_invested_input, 
     amount_goal_input, 
     min_nr_assets,
     submit
     ]
)


# # OUTPUTS
df = pd.DataFrame({
    "Assets": assets,
    "Amount": [0]*len(assets)
})

fig_pie = px.pie(df, values="Amount", names = 'Assets')

fig_line = px.line()

outputs = html.Div(
    [html.Div(id = 'top_text', children = "You haven't submitted inputs yet"),
     dcc.Graph(
        id='pie_chart',
        figure=fig_pie
    ),
    html.Div(id = 'middle_text'),
    dcc.Graph(
     id = 'line_chart',
     figure = fig_line
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
    'Moderate'      : 0.3,
    'Conservative'  : 0.03
}

@callback(
    Output("top_text", 'children'),
    Output('pie_chart', 'figure'),
    Output('line_chart', 'figure'),
    Input('submit-val', 'n_clicks'),
    State('risk_level', 'value'),
    State('years', 'value'),
    State('amount_invested','value'),
    State('goal_amount','value'),
    State('monthly_or_not','value'),
    State('min_assets','value')
)
def update_output(submission_number, risk, years, amount_invested, min_return, installment_flag, nr_assets):

    if installment_flag == 1:
        amount_invested = amount_invested * 12 * years

    if submission_number is None or submission_number == 0:
        return "No data yet", no_update, no_update
    
    min_return_function = min_return - amount_invested
    
    max_risk = risk_dict[risk]

    print(years, min_return_function, max_risk, amount_invested, covariance, mean_returns, assets, installment_flag, nr_assets)

    m, investment_amount = creating_and_running_optimizer(years, min_return_function, max_risk, amount_invested, covariance, mean_returns, assets, installment_flag, nr_assets)

    if m.status == GRB.OPTIMAL:
        total_return = m.objVal
        print('\nPortfolio Return: %g' % total_return)
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
        return text, px.pie(), px.line()

    
    text = ['We have chosen risk level: {}'.format(risk),
            html.Br(), 
            'outcome of optimizer is {}'.format(m.objVal)
            ]
    

    df = pd.DataFrame({
        'Assets': investment_amountx.keys(), 
        'Amount': investment_amountx.values(), 
        })

    fig_pie = px.pie(df, values="Amount", names = 'Assets')

    lowest_range = []
    regular_range = []
    highest_range = []

    if installment_flag==0:
        for year in range(years):
            reg_return = 0
            low_return = 0
            high_return =0
            for a in assets:
                reg_return_a = investment_amountx[a]*((1+mean_returns[a])**(12*year))
                reg_return += reg_return_a

                low_return_a = investment_amountx[a]*((1+(mean_returns[a]-max_risk))**(12*year))
                low_return += low_return_a
                
                high_return_a = investment_amountx[a]*((1+(mean_returns[a]+max_risk))**(12*year))
                high_return += high_return_a
                
            regular_range.append(reg_return)
            lowest_range.append(low_return)
            highest_range.append(high_return)

    else:
        for year in range(years):
            #min return accepted - monthly instalment version
            reg_return = 0
            low_return = 0
            high_return = 0
            for a in assets:

                reg_return_a = investment_amountx[a]/(12*years) * (1+ mean_returns[a])**(12*(years-year))
                reg_return += reg_return_a

                low_return_a = investment_amountx[a]/(12*years) * (1+ mean_returns[a] - max_risk)**(12*(years-year))
                low_return += low_return_a

                high_return_a = investment_amountx[a]/(12*years) * (1+ mean_returns[a] + max_risk)**(12*(years-year))
                high_return += high_return_a

            regular_range.append(reg_return)
            lowest_range.append(low_return)
            highest_range.append(high_return)

    df_line = pd.DataFrame({
         "Years": range(0, years, 1), 
         "Poor market conditions": lowest_range,
         "Intermediate market conditions": regular_range,
         "Good market conditions": highest_range
    })

    df_line = df_line.set_index('Years').stack().reset_index()
    df_line.rename({'level_1':'Market Conditions', 0:"Value"}, inplace=True, axis=1)
    print(type(df_line))
    print(df_line.head())

    fig_line = px.line(df_line, x = 'Years', y = 'Value', color = 'Market Conditions')
    fig_line.update_traces(mode="markers+lines", hovertemplate=None)
    fig_line.update_layout(hovermode="x unified")

    
    return text, fig_pie, fig_line





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