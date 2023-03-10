# %% [markdown]
# # Introduction

# %% [markdown]
# ### ***Purpose***
# Knowing how to invest personal savings is important for maximizing wealth for all: individuals, households and institutions. And it goes far beyond just locking money in a savings account. With this optimization problem we are addressing the needs to faciliate personal investment decision-making. 
# 
# 
# ### ***Method***
# We consider a number of assets in which one could invest and devise a model to optimize a portfolio which generates the highest return for a given level of risk. 
# We appreciate that users can have different levels of target return, time horizons and risk-averseness. 
# For this purpose, we run the model for several different scenarios in which we adjust for different metrics. 
# 
# <img src="citi-bike.jpg" width="500">

# %%
# Import various packages
import pandas as pd
import numpy as np
import seaborn as sns # general visualization package 
import matplotlib.pyplot as plt # general visualization package 
#next command allows you to display the figures in the notebook 

# %%
# Import the gurobi package
import gurobipy as gp
from gurobipy import GRB,quicksum
import datetime

# %% [markdown]
# # Data

# %%
riskfree = pd.read_csv('DAM_portfolio_optimization/data/riskfree.csv')
bitcoin = pd.read_csv('DAM_portfolio_optimization/data/bitcoin.csv')
gold = pd.read_csv('DAM_portfolio_optimization/data/Gold.csv')
ftse = pd.read_csv('DAM_portfolio_optimization/data/FTSE.csv')
bank_rates = pd.read_excel('DAM_portfolio_optimization/data/bank_rates.xlsx')
house_prices = pd.read_excel('DAM_portfolio_optimization/data/house_prices.xlsx')

# %%
riskfree = riskfree.dropna()
bitcoin = bitcoin.dropna()
gold = gold.dropna()
ftse = ftse.dropna()
bank_rates = bank_rates.dropna()
house_prices = house_prices.dropna()

# %%
riskfree['Date'] = pd.to_datetime(riskfree['Date'], format='%b-%y')
riskfree = riskfree.sort_values(by='Date')

# %%
bitcoin['Date'] = pd.to_datetime(bitcoin['Date'])
bitcoin = bitcoin.sort_values(by="Date")

# %%
gold['Date'] = pd.to_datetime(gold['Date'])
gold = gold.sort_values(by="Date")

# %%
ftse['Date'] = pd.to_datetime(ftse['Date'])
ftse = ftse.sort_values(by="Date")

# %%
bank_rates['Rate'] = bank_rates['Rate']/12

# %%
house_prices['Date'] = pd.to_datetime(house_prices['Date'])
house_prices = house_prices.sort_values(by="Date")

# %%
values = pd.DataFrame()

# %%
values.index = riskfree['Date'].dt.strftime('%m/%Y')
values['riskfree'] = riskfree['Price'].values
values['bitcoin'] = bitcoin['Open'].values
values["gold"] = gold['Price'].values
values["ftse"] = ftse['Price'].values
values['ftse'] = values['ftse'].str.replace(',','')
values["ftse"] = values["ftse"].astype(float)
values["house_prices"] = house_prices['PX_MID'].values
values["bank_rates"] = bank_rates['Rate'].values

# %%
returns = pd.DataFrame()
returns = values.pct_change(1)
returns['bank_rates'] = values['bank_rates']


# %%
mean_returns = returns.mean()
mean_returns = mean_returns.to_dict()

# %%
mean_returns['riskfree'] = 0.00322 # current yearly rate is 3.864%, thus monthly rate is 3.864/12

# %%
variance = returns.var()
variance = variance.to_dict()

# %%
variance['riskfree'] = 0 # assume

# %%
covariance = values.cov()

# %%
covariance['riskfree'] = 0
covariance.iloc[0] = 0


# %%

time_frame = 1 # In percentage standard deviation required
min_return = 5000
max_risk = 10
amount_invested = 100000

# %%
def printSolution(m, investment_amount, assets):
    if m.status == GRB.OPTIMAL:
        print('\nPortfolio Return: %g' % m.objVal)
        print('\nInvestment Amount:')
        investment_amountx = m.getAttr('x', investment_amount) 
        for a in assets:            
                print('%s %g' % (a, investment_amountx[a]))
    else:
        print('No solution:', m.status)

# %%

assets = ['riskfree', 'bitcoin', 'gold', 'ftse', 'house_prices', 'bank_rates'] 

def creating_and_running_optimizer(time_frame, min_return, max_risk, amount_invested, covariance, returns, assets):

    # Create a new model:
    m = gp.Model("portfolio")

    returns = mean_returns

    risks = variance

    investment_amount = m.addVars(assets, vtype=GRB.INTEGER, lb = 0, name = "investment_amount")


    #min return accepted       
    m.addConstr((quicksum(investment_amount[a]*((1+returns[a])**(12*time_frame)) for a in assets)-amount_invested >= min_return),
                name = "minimum return accepted")

    #max risk accepted 
    m.addConstr((quicksum(investment_amount[a1]*investment_amount[a2]*covariance.loc[a1,a2]/((amount_invested)**2) 
                        for a1 in assets for a2 in assets)) + 0.000718 <= ((max_risk*(quicksum(investment_amount[a1] for a1 in assets))/amount_invested/100)**2), name="maximum risk accepted")

    #0.000718(The market varaince calculated using UK GDP numbers) is added to the risk limit
    
    #sum of investments
    m.addConstr((quicksum(investment_amount[a1] for a1 in assets)) == amount_invested, name="sum of investments")

    # Objective function:
    m.setObjective(quicksum(investment_amount[a]*((1+returns[a])**(12*time_frame)) for a in assets) - amount_invested, 
                GRB.MAXIMIZE)

    #add the objective function to minimize risk 
    #send Vivian the output from running the model


    m.optimize()

    return m, investment_amount


