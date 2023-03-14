import pandas as pd
import numpy as np





def utilization_rate(contract_balance, contract_lend):
    util_rate = .5
    over_borrow = False
    if contract_balance> 0 and contract_balance>contract_lend:
        util_rate = contract_lend/contract_balance
    elif contract_balance > 0 and contract_balance < contract_lend:
        over_borrow = True
    return over_borrow, util_rate

def intrest_rate(util_rate ,util_optimal, base_rate, slope1, slope2, over_borrow):
    
    i_rate = base_rate + slope1
    
    if over_borrow == False:
        if util_rate<= util_optimal:
            i_rate = base_rate + slope1*(util_rate/util_optimal)
        if util_rate >util_optimal:
            i_rate = base_rate +slope1 +slope2*((util_rate -util_optimal)/(1-util_optimal))
    elif over_borrow == True:
        i_rate = i_rate + slope1 + slope2*100

    return i_rate

def intrest_to_pay(intrest_rate, borrow_amount):

    intrest = (1+intrest_rate/365)*borrow_amount

    return intrest
                                                

