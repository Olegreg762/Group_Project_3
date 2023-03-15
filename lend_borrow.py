import streamlit as st
from dataclasses import dataclass
import yfinance as yf
#from crypto_wallet import generate_account, get_balance, send_transaction, access_treasury_account
from web3 import Web3
import time
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import pandas as pd
import Interest_rate as it_rate
from notification_manager import send_notification

######################################################
###### Define Variables and Load Smart Contract ######
######################################################

load_dotenv()

# twilio_number = os.getenv("VIRTUAL_TWILIO_NUMBER")
# user_number = os.getenv("VERIFIED_NUMBER")
# twilio_sid = os.getenv("TWILIO_SID")
# twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# creates a Web3 instance of the Ganache network on local machine
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

st.set_page_config(layout='wide')


 #Smart Contract connection
@st.cache_resource
def load_contract():
    ### UPDATE CONTRACT ABI INFO AFTER DEPLOYMENT ###
    with open (Path('pylend_abi.json')) as f:
        pylend_abi = json.load(f)
    
    #contract_address=os.getenv('') 
    ### UPDATE CONTRACT ADDRESS AFTER DEPLOYMENT ###
    contract_address = os.getenv('SMART_CONTRACT_ADDRESS')

    contract = w3.eth.contract(
        address=contract_address,
        abi=pylend_abi
    )

    return contract

# Initaliize contract
contract = load_contract()

# Define intrest rate variables

# Define default util_rate
util_rate = .5

# Define optimal util rate
util_optimal = 0.8

# Define base rate
base_rate = .01

# Define slope 1, for interest rate calc when util_rate <= util_opt
slope1 = 0.02

# Define slope 2, for intrest rate calc when util_rate > util_opt
slope2 = 1.5

# Error Flag if the Util rate is greater than 1
over_borrow = False

lend_interest_rate = base_rate + slope1/2
borrow_interest_rate = base_rate +slope1

######################################################
######################################################
############ Solidity Contract Functions #############

# Functio to interact with solidity contract
def solidity_function(func, amount=None):
    user_account = w3.eth.accounts[0]
    # Function for lending
    if func =='lend':
        lend_amount = amount
        lend_amount_wei = Web3.toWei(lend_amount*10**18, 'wei')
        lend = contract.functions.lend().transact({'value': lend_amount_wei,'from': w3.eth.accounts[0]})
        lend_balance = contract.functions.lendBalance().call()
        return lend_balance
    # Function for borrowing
    elif func =='borrow':
        borrow_amount = amount
        borrow_amount_wei = Web3.toWei(borrow_amount*10**18, 'wei')
        borrow = contract.functions.borrow(borrow_amount_wei).transact({'from': w3.eth.accounts[0]})
        borrow_balance = contract.functions.borrowBalance(user_account).call()
        return borrow_balance
    # Function to repay borrow_balance
    elif func =='repay':
        repay_amount = amount
        repay_amount_wei = Web3.toWei(repay_amount*10**18, 'wei')
        repay = contract.functions.repay(repay_amount_wei).transact({'value': repay_amount_wei, 'from': w3.eth.accounts[0]})
        new_borrow_balance = contract.functions.borrowBalance(user_account).call()
        return new_borrow_balance
    # Function to withdraw lend_balance
    elif func == 'withdraw':
        withdraw_amount = amount
        withdraw_amount_wei = Web3.toWei(withdraw_amount*10**18, 'wei')
        withdraw = contract.functions.withdraw(withdraw_amount_wei).transact({'from': w3.eth.accounts[0]})
        withdraw_balance = contract.functions.borrowBalance(user_account).call()
        return withdraw_balance
    # Check user_balance
    elif func == 'user_balance':
        return w3.eth.get_balance(w3.eth.accounts[0])/10**18
    # Check borrow_balance
    elif func == 'borrow_balance':
        return contract.functions.borrowBalance(w3.eth.accounts[0]).call()/10**18
    # Check lend_balance
    elif func == 'lend_balance':
        return contract.functions.lendBalance().call()/10**18
    # Check treasury_balance
    elif func == 'treasury_balance':
        return w3.eth.get_balance(os.getenv('SMART_CONTRACT_ADDRESS'))/10**18
    
######################################################    
######################################################
######################################################

# Create Title for streamlit app
st.markdown("<h1 style='text-align: center;'><FONT COLOR=blue><i>Py</i><FONT COLOR=green>Bo<FONT COLOR=blue>Lend</h1>",unsafe_allow_html=True)

# Pulls data using the yfinance API to determine liquidation risk based on price movement.
eth_price = yf.download(tickers='ETH-USD',period='1d', interval='5m',rounding=True).drop(columns=['Adj Close','Open','High','Low','Volume'])
eth_price['Percent Change']=eth_price['Close'].pct_change()
percent_change=eth_price['Percent Change'].mean()*100

# Initialize column interface for streamlit
treasury_col, functions_col, account_col = st.columns([1,4.75,1])

##
## treasury_col and account_col at bottom of file so the balances updates after actions
##

# Column that contains the functions to interact with smart contract
with functions_col:
    
    st.subheader('The :violet[Premier] ETH Lending and Borrowing Application')

    # Create the Tabs for streamlit
    lend_tab,borrow_tab,repay_tab,withdraw_tab,balances_tab,time_tab = st.tabs(['Lend', 'Borrow', 'Repay', 'Withdraw', 'Balances', 'Time Advance'])

    # Creates Lend Tab
    with lend_tab:

        st.header('Lend')   

        lend_amount = st.number_input('Enter the amount you want to lend (in ETH):')
        if lend_amount != 0:
            st.write(f'{lend_interest_rate:.2}% Lending Interest' )
        else:
            lend_interest_rate

        
        if st.button('Complete Lend',key='lend'):

            # sending loan to the TREASURY_ADDRESS
            solidity_function('lend', lend_amount)

            st.write(f'{lend_amount} has been deducted from your personal wallet.')    
            st.write(f'We owe you {lend_amount} + {lend_interest_rate}% interest.')   
            st.write('New Balance:', solidity_function('user_balance'))

            # updates the balance of the TREASURY_ADDRESS
            solidity_function('treasury_address')
            st.write(f'The new treasury balance is:' , solidity_function('treasury_balance'), 'ETH')

            # Sends SMS notification - NOTE the line below works, but commenting out until closer to presentation to limit trial uses
            # send_notification(f"Transaction confirmed. You have received your deposit of {lend_amount}ETH. The amount you may borrow has increased by {lend_amount * 0.8}ETH.") 


    # Creates Borrow Tab
    with borrow_tab:
        st.header('Borrow')
        borrow_amount = st.number_input('Enter the amount you want to borrow (in ETH):')
        if borrow_amount != 0:
            st.write(f'{(borrow_interest_rate):.2}% Borrow Interest')
        else:
            # Choose and insert default value for borrow_interest_rate
            borrow_interest_rate
            

        if st.button('Complete Borrow',key='borrow'):

            # sending loan to the TREASURY_ADDRESS
            solidity_function('borrow', borrow_amount)
            #balance = user_balance
            st.write(f'{borrow_amount} ETH has been sent to your personal wallet.')    
            st.write(f'You owe us {borrow_amount} + {(borrow_interest_rate * 2):.2}% interest.')    
            st.write('New Borrow Balance:', solidity_function('borrow_balance'))    
            # updates the balance of the TREASURY_ADDRESS
            solidity_function('treasury_address')
            st.write(f'The new treasury balance is:' , solidity_function('treasury_balance'), 'ETH')

    # Creates Repay Tab
    with repay_tab:
        st.header('Repay')
        st.write(f'Amount Owed:', solidity_function('borrow_balance'),'ETH')
        repay_amount = st.number_input('Enter amount to repay')
        if st.button('Submit',key='repay'):
            solidity_function('repay', repay_amount)
            st.write(f'{repay_amount} has been repayed to the treasury for you debts.')    
            #  @TODO calculate and track interest_accrued    
            st.write(f'New Borrow Balance:', solidity_function('borrow_balance'), 'ETH')
    
    with withdraw_tab:
        st.header('Withdraw')
        st.write(f'All Borrows must be paid before withdraw. Current Borrow Balance:', solidity_function('borrow_balance'),'ETH')
        
        withdraw_amount = st.number_input('Amount to Withdraw')
        if st.button('Submit'):
            solidity_function('withdraw', withdraw_amount)
            st.write('New Borrow Balance:', solidity_function('borrow_balance'),'ETH')

    #Creates Balances tab
    with balances_tab:
        st.header('Balances')
        if st.button('Get Balances'):
            st.write(f' Account Balance:', solidity_function('user_balance'), 'ETH')
            st.write(f'Borrow Balance:', solidity_function('borrow_balance'), 'ETH')
            st.write(f'Lend Balance:', solidity_function('lend_balance'), 'ETH')



    with time_tab:
        st.header('FOR TESTING ONLY')
        st.write('This tab to be REMOVED before deployment')
        st.write('Only used to show how Lend/Borrow interest accrual functions')

        if 'count' not in st.session_state:
            st.session_state.count = 0

        increment = st.button('Advance Time')
        if increment:

            st.session_state.count += 1
            treasury_balance = solidity_function('treasury_balance')
            borrow_balance = solidity_function('borrow_balance')
            over_borrow, util_rate = it_rate.utilization_rate(treasury_balance,borrow_balance)
            borrow_interest_rate = it_rate.interest_rate(util_rate, util_optimal, base_rate, slope1, slope2, over_borrow)
            lend_interest_rate = borrow_amount/2

            ####
            lend_balance = solidity_function('lend_balance')
            lend_interest_amount = it_rate.interest_to_pay(lend_interest_rate, borrow_balance, 0)
            treasury_balance += lend_interest_amount
            lend_balance += lend_interest_amount

            ###
            borrow_interest_amount = it_rate.interest_to_pay(borrow_interest_rate, borrow_balance, 0)
            borrow_balance += borrow_interest_amount
            

        st.write('Interest Time', st.session_state.count)
        st.write('Lend Intrest Rate',lend_interest_rate )
    

# Column that displays treasury data
with treasury_col:
    st.header('Treasury Balance') 
    st.write(solidity_function('treasury_balance'), 'ETH')
    # liquidate signal
    if percent_change >= 1:
        #st.write(f'Average Price Change :red[{percent_change:.3f}]%')
        st.header('Liquidate Risk')
        st.write(':red[High]')
    elif percent_change <= 1:
        #st.write(f'Average Price Change :green[{percent_change:.3f}]%')
        st.header('Liquidate Risk')
        st.write(':green[Low]')

# Column that displays user account balance
with account_col:
# Loads account credentials
    if solidity_function('user_balance') != None:
        st.header('Account Status')
        st.write(':green[Connected]')
        st.header('Account Balance')
        st.write(solidity_function('user_balance'), 'ETH')
    else:
        st.write('Please ensure your Mneumonic phrase is saved in a .env in this same directory.')
        st.write('Then restart this application.')