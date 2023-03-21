import streamlit as st
import yfinance as yf
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
################ Load Smart Contract #################

load_dotenv()

# Creates a Web3 instance of the Ganache network on local machine
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

st.set_page_config(layout='wide')


# Smart Contract connection and store in in Streamlit cache
@st.cache(allow_output_mutation=True)
def load_contract():
    ### UPDATE CONTRACT ABI INFO AFTER DEPLOYMENT ###
    with open (Path('pylend_abi.json')) as f:
        pylend_abi = json.load(f)
    
    ### Update contract address after deployment ###
    contract_address = os.getenv('SMART_CONTRACT_ADDRESS')

    contract = w3.eth.contract(
        address=contract_address,
        abi=pylend_abi
    )

    return contract

# Initialize contract
contract = load_contract()


######################################################
########## Define intrest rate variables #############

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

# Error flag if the util rate is greater than 1
over_borrow = False

lend_interest_rate = base_rate + slope1/2
borrow_interest_rate = base_rate +slope1

######################################################
############ Solidity Contract Functions #############


# Function to interact with solidity contract
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
    # Function that does that interest transactions
    elif func == 'interest':
    # Send interest to treasury balance
        interest_amount = amount
        interest_amount_wei = Web3.toWei(interest_amount*10**18, 'wei')
        interest = contract.functions.contractStart().transact({'value': interest_amount_wei,'from': w3.eth.accounts[0]})
    # Send interest to user lend balance
        lend = contract.functions.lend().transact({'value': interest_amount_wei,'from': w3.eth.accounts[0]})
        lend_balance = contract.functions.lendBalance().call()
        interest_balance = interest_amount
        return interest_balance
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
############### Main Streamlit Application ###########


# Create title for Streamlit app
st.markdown("<h1 style='text-align: center;'><FONT COLOR=blue><i>Py</i><FONT COLOR=green>Bo<FONT COLOR=blue>Lend</h1>",unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'><FONT COLOR=green>------------------------------<FONT COLOR=blue>------------------------------</h1>",unsafe_allow_html=True)

# Pulls data using the yfinance API to determine liquidation risk based on price movement.
eth_price = yf.download(tickers='ETH-USD',period='1d', interval='5m',rounding=True).drop(columns=['Adj Close','Open','High','Low','Volume'])
eth_price['Percent Change']=eth_price['Close'].pct_change()
percent_change=eth_price['Percent Change'].mean()*100

# Initialize column interface for Streamlit
treasury_col, functions_col, account_col = st.columns([1,4.75,1])

###
## treasury_col and account_col at bottom of file so the balances update after actions
###

# Column that contains the functions to interact with Smart Contract
with functions_col:
    
    st.subheader('The :violet[Premier] ETH Lending and Borrowing Application')

    # Create the tabs for Streamlit
    lend_tab,borrow_tab,repay_tab,withdraw_tab,balances_tab,time_tab = st.tabs(['Lend', 'Borrow', 'Repay', 'Withdraw', 'Balances', 'Time Advance'])

    # Creates Lend tab
    with lend_tab:

        st.header('Lend')   

        lend_amount = st.number_input('Enter the amount you want to lend (in ETH):')

        notification_number = st.text_input('Enter your phone number to receive confirmation via text message:')
        
        if lend_amount != 0:
            st.write(f'{lend_interest_rate:.2}% Lending Interest' )
        else:
            lend_interest_rate

        
        if st.button('Complete Lend',key='lend'):

            # Sending loan to the TREASURY_ADDRESS
            solidity_function('lend', lend_amount)

            st.write(f'{lend_amount} has been deducted from your personal wallet.')    
            st.write(f'We owe you {lend_amount} + {lend_interest_rate}% interest.')   

            # Updates the balance of the TREASURY_ADDRESS
            solidity_function('treasury_address')

            # Sends SMS notification 
            if notification_number != None:
                try:
                    send_notification(f"Transaction confirmed. You have received your deposit of {lend_amount}ETH. The amount you may borrow has increased by {lend_amount * 0.8}ETH.", f"+1{notification_number}") 
                except:
                    st.write("The number you entered may not be valid, but the above information confirms your transaction.")


    # Creates Borrow tab
    with borrow_tab:
        st.header('Borrow')
        borrow_amount = st.number_input('Enter the amount you want to borrow (in ETH):')
        if borrow_amount != 0:
            st.write(f'{(borrow_interest_rate):.2}% Borrow Interest')
        else:
            # Choose and insert default value for borrow_interest_rate
            borrow_interest_rate
            

        if st.button('Complete Borrow',key='borrow'):

            # Sending loan to the TREASURY_ADDRESS
            solidity_function('borrow', borrow_amount)
            
            st.write(f'{borrow_amount} ETH has been sent to your personal wallet.')    
            st.write(f'You owe us {borrow_amount} + {(borrow_interest_rate * 2):.2}% interest.')    
            st.write('New Borrow Balance:', solidity_function('borrow_balance'))    
            # Updates the balance of the TREASURY_ADDRESS
            solidity_function('treasury_address')
           
    # Creates Repay tab
    with repay_tab:
        st.header('Repay')
        st.write(f'Amount Owed:', solidity_function('borrow_balance'),'ETH')
        repay_amount = st.number_input('Enter amount to repay')
        if st.button('Submit',key='repay'):
            solidity_function('repay', repay_amount)
            st.write(f'{repay_amount} has been repayed to the treasury for you debts.')    
               
            st.write(f'New Borrow Balance:', solidity_function('borrow_balance'), 'ETH')
    
    # Create Withdraw tab
    with withdraw_tab:
        st.header('Withdraw')
        st.subheader('All Borrows must be paid before withdrawal.')
        st.write('Current Borrow Balance:', solidity_function('borrow_balance'),'ETH')
        st.write('Current Lend Balance:', solidity_function('lend_balance'),'ETH')
        withdraw_amount = st.number_input('Amount to Withdraw')
        if st.button('Submit'):
            solidity_function('withdraw', withdraw_amount)
            st.write('New Borrow Balance:', solidity_function('borrow_balance'),'ETH')

    # Creates Balances tab
    with balances_tab:
        st.header('Balances')
        if st.button('Get Balances'):
            st.write(f' Account Balance:', solidity_function('user_balance'), 'ETH')
            st.write(f'Borrow Balance:', solidity_function('borrow_balance'), 'ETH')
            st.write(f'Lend Balance:', solidity_function('lend_balance'), 'ETH')
    
    # Create Time Advance tab
    with time_tab:
        st.header('FOR TESTING ONLY')
        st.write('This tab to be REMOVED before deployment')
        st.write('Only used to show how Lend/Borrow interest accrual functions')

        if 'count' not in st.session_state:
            st.session_state.count = 0

        increment = st.button('Advance Time')
        if increment:

            st.session_state.count += 1

            #calculate utilization rate
            over_borrow, util_rate = it_rate.utilization_rate(solidity_function('treasury_balance'),solidity_function('borrow_balance'))

            #set borrow interest rate
            borrow_interest_rate = it_rate.interest_rate(util_rate, util_optimal, base_rate, slope1, slope2, over_borrow)

            #set lend interest rate
            lend_interest_rate = borrow_interest_rate/2

            borrow_interest_amount = (it_rate.interest_to_pay(borrow_interest_rate, solidity_function('borrow_balance'), 0))
            
            st.write('Interest Paid to us',solidity_function('interest',borrow_interest_amount/2))
            st.write('Interest Paid to you', borrow_interest_amount/2 )

        st.write('Interest Time', st.session_state.count)
        st.write('Lend Intrest Rate',lend_interest_rate )
    

# Column that displays treasury data
with treasury_col:
    st.header('Treasury Balance') 
    st.write(solidity_function('treasury_balance'), 'ETH')
    # liquidate signal
    if percent_change >= 1:
        st.header('Liquidate Risk')
        st.write(':red[High]')
    elif percent_change <= 1:
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