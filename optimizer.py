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
import statistics
import folium # visualisation package for spatial data (plot of maps)
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
riskfree = pd.read_csv('data/riskfree.csv')
bitcoin = pd.read_csv('data/bitcoin.csv')
gold = pd.read_csv('data/Gold.csv')
ftse = pd.read_csv('data/FTSE.csv')
bank_rates = pd.read_excel('data/bank_rates.xlsx')
house_prices = pd.read_excel('data/house_prices.xlsx')

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
bank_rates

# %%
house_prices['Date'] = pd.to_datetime(house_prices['Date'])
house_prices = house_prices.sort_values(by="Date")

# %%
values = pd.DataFrame()

# %%
# riskfree = pd.read_csv('riskfree.csv')
# bitcoin = pd.read_csv('bitcoin.csv')
# gold = pd.read_csv('Gold.csv')
# ftse = pd.read_csv('FTSE.csv')
# bank_rates = pd.read_excel('bank_rates.xlsx')
# house_prices = pd.read_excel('house_prices.xlsx')
bank_rates

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
values

# %%
returns = pd.DataFrame()
returns = values.pct_change(1)
returns['bank_rates'] = values['bank_rates']

# %%
returns

# %%
mean_returns = returns.mean()
mean_returns = mean_returns.to_dict()

# %%
mean_returns['riskfree'] = 0.00322 # current yearly rate is 3.864%, thus monthly rate is 3.864/12
mean_returns

# %%
variance = returns.var()
variance = variance.to_dict()

# %%
variance['riskfree'] = 0 # assume
variance

# %%
covariance = values.cov()

# %%
covariance['riskfree'] = 0
covariance.iloc[0] = 0
covariance

# %% [markdown]
# ## User-defined input

# %% [markdown]
# ## Vivian's code

# %%
#vivan's code - linked to extract the values that were user's input from the dashboard

#our temporary input
# time_frame = 2

# amount_invested = 1000 

# min_return = 5000

# max_risk = 0.1

time_frame = 12
min_return = 5000
max_risk = 10
amount_invested = 100000

# %% [markdown]
# ## Model creation

# %%
# Create a new model:
m = gp.Model("portfolio")

# %% [markdown]
# ## Data

# %% [markdown]
# *Define the dictionaries containing the data:*

# %%
# Fixed inputs
assets = ['riskfree', 'bitcoin', 'gold', 'ftse', 'house_prices', 'bank_rates'] 

# will need to get real data from Ishaan to substitute below:
returns = mean_returns

risks = variance

# %% [markdown]
# ## Formulate the optimal allocation strategy as an integer program

# %% [markdown]
# 
# 1. **Decision variables:** We create a decision variable $x_a$ for the amount invested for each asset $a \in {\rm assets}$.
# This means that we have the following decision variables: $x_{crypto}, x_{real estate}, x_{FTSE},x_{tech stocks}, x_{savings account}, x_{bond 3m}, x_{bond 1 yr}, x_{bond 5 yr},x_{bond 10 yr}$. The quantity of the optimal budget allocation over assets is unknown.
# 
# 
# 2. **Constraints:** We need to ensure that the total budget spent across all the keywords does not exceed the fixed amount to be invested that was entered by the user. Mathematically, this requirement is expressed using a linear constraint: 
# <br><br>
# $$  x_{crypto} + x_{real estate} + x_{FTSE} + x_{tech stocks} + x_{savings account} + x_{bond 3m}+x_{bond 1 yr}+x_{bond 5 yr}+x_{bond 10 yr} \leq \quad money\quad invested$$
# <br>
# In this constraint, the total money invested spent should not exceed the restriction of the user input.
# 
#     
# 3. **Objective function:** Now, we need to select the objective function. *What should we optimize for?* The goal is find a combination of money allocation for each asset that maximizes the final return. It is shown with the following expression:
# 
# <br><br>
# $$  \max_{x_a}  \quad\quad\quad  x_{crypto}\cdot(1+return rate_{crypto})^{time frame} + x_{real estate}\cdot(1+return rate_{real estate})^{time frame} + x_{FTSE}\cdot(1+return rate_{FTSE})^{time frame} + x_{tech stocks}\cdot(1+return rate_{tech stocks})^{time frame} + x_{savings account}\cdot(1+return rate_{savings account})^{time frame} + x_{bond 3m}\cdot(1+return rate_{bond 3m})^{time frame} + x_{bond 1 yr}\cdot(1+return rate_{bond 1 yr})^{time frame} + x_{bond 5 yr}\cdot(1+return rate_{bond 5 yr})^{time frame} + x_{bond 10 yr}\cdot(1+return rate_{bond 10 yr})^{time frame}$$
# <br>
# 
# In this function, we maximize the return for a given time horizon specified by the user (ie. *time_frame* refers to the time period for which the user is ready to have their money locked in the investment portfolio). 
# 
# Shortly, we can express the function as following:
# 
# $$ \max_{x_a} \quad\quad\quad \sum_{a=1}^{n} X_a \cdot (1+return rate_a)^{time frame}$$
# 

# %% [markdown]
# ## Decision variables

# %%
investment_amount = m.addVars(assets, vtype=GRB.INTEGER, lb = 0, name = "investment_amount")

# %% [markdown]
# ## Constraints 

# %% [markdown]
# Add constraints for:
# 
# 1) minimum output return that is accepted (ie. that the output should be greater than or equal to the return desired by the user)
# 
# 2) maximum level of risk accepted (ie. that the output portfolio should have risk that does not exceed the maximum risk specified by the user)

# %%
#proxy values
# time_frame = 10
# min_return = 0.03
# max_risk = 0.1
# amount_invested = 10000

#min return accepted       
m.addConstr((quicksum(investment_amount[a]*((1+returns[a])**(12*time_frame)) for a in assets)-amount_invested >= min_return),
             name = "minimum return accepted")

#max risk accepted
# m.addConstr((quicksum(investment_amount[a1]*investment_amount[a2]*risks[a1]*risks[a2]*covariance.loc[a1,a2]/((amount_invested)**2) 
#                        for a1 in assets for a2 in assets)) <= max_risk, name="maximum risk accepted")

#max risk accepted corrected
m.addConstr((quicksum(investment_amount[a1]*investment_amount[a2]*covariance.loc[a1,a2]/((amount_invested)**2) 
                       for a1 in assets for a2 in assets)) <= (max_risk**2), name="maximum risk accepted")

#sum of investments
m.addConstr((quicksum(investment_amount[a1] for a1 in assets)) == amount_invested, name="sum of investments")

# %% [markdown]
# ## Objective

# %% [markdown]
# Formulate the objective function 

# %%
# Objective function:
m.setObjective(quicksum(investment_amount[a]*((1+returns[a])**(12*time_frame)) for a in assets), 
              GRB.MAXIMIZE)

#add the objective function to minimize risk 
#send Vivian the output from running the model

# %% [markdown]
# ## Solve

# %% [markdown]
# After having formulated and implemented the integer program, we can now optimize the portfolio allocation and printout the optimal return:

# %%
# Run the optimization
def printSolution():
    if m.status == GRB.OPTIMAL:
        print('\nPortfolio Return: %g' % m.objVal)
        print('\nInvestment Amount:')
        investment_amountx = m.getAttr('x', investment_amount) 
        for a in assets:            
                print('%s %g' % (a, investment_amountx[a]))
    else:
        print('No solution:', m.status)
        
m.optimize()
printSolution()

# %%
time_frame

# %%
risks

# %%
returns

# %%
returns.median()

# %%
returns.mean()


