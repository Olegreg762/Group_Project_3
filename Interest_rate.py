import pandas as pd
import numpy as np

# function used to calculate utilization rate of assets 

def utilization_rate(contract_balance, contract_lend):

    # sets default rate if the function errors out
    util_rate = .5
    over_borrow = False

    # tests contract balance and calculates Util rate

    if contract_balance>= 0 and contract_balance>contract_lend:
        util_rate = contract_lend/contract_balance
    elif contract_balance >= 0 and contract_balance < contract_lend:
        over_borrow = True
    return over_borrow, util_rate


# function to calculate intrest rate. Uses Aava method. See https://docs.aave.com/risk/liquidity-risk/borrow-interest-rate
def interest_rate(util_rate ,util_optimal, base_rate, slope1, slope2, over_borrow):
    
    #sets default rate 
    i_rate = base_rate + slope1
    
    # Test if there is an over-borrow situation
    if over_borrow == False:

        # if the utilization rate is less than the optimal rate
        if util_rate<= util_optimal:
            i_rate = base_rate + slope1*(util_rate/util_optimal)

        # if the utilization rate is greater than the optimal rate    
        elif util_rate >util_optimal:
            i_rate = base_rate +slope1 +slope2*((util_rate -util_optimal)/(1-util_optimal))
    
    # sets the intrest if the over borrow is high
    elif over_borrow == True:
        i_rate = i_rate + slope1 + slope2*100

    return i_rate


# calculats the intrest to be paid on a daily basis
def interest_to_pay(interest_rate, borrow_amount, gas_fee_est):

    interest = (1+interest_rate/365)*borrow_amount

    return interest
                                                

