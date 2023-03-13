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

######################################################
###### Define Variables and Load Smart Contract ######
######################################################

load_dotenv()

# creates a Web3 instance of the Ganache network on local machine
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

st.set_page_config(layout='wide')

 #Smart Contract connection
@st.cache(allow_output_mutation=True)
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

# Load user account
user_account = w3.eth.accounts[0]

# Load user account balance
user_balance = w3.eth.get_balance(w3.eth.accounts[0])/10**18

# Load contract(treasury) address
treasury_address = os.getenv('SMART_CONTRACT_ADDRESS')

# Load contract(treasury) balance
treasury_balance = w3.eth.get_balance(os.getenv('SMART_CONTRACT_ADDRESS'))/10**18

# Define User Borrow Balance
borrow_balance = contract.functions.borrowBalance(user_account).call()

# Define User Lend Balance
lend_balance = contract.functions.lendBalance().call()

######################################################
######################################################
######################################################

st.title(':green[------------------------------------]:blue[$PyBo$]:green[Lend]:blue[------------------------------------]')


eth_price = yf.download(tickers='ETH-USD',period='1day', interval='1m',rounding=True).drop(columns=['Adj Close','Open','High','Low','Volume'])
eth_price['Percent Change']=eth_price['Close'].pct_change()
percent_change=eth_price['Percent Change'].mean()*100

# Initialize column interface for streamlit
treasury_col, functions_col, account_col = st.columns([1,4.75,1])

# Column that displays treasury data
with treasury_col:
    st.header('Treasury Balance') 
    st.write(f'{treasury_balance} ETH')
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
    #user_account = generate_account()
    if user_balance != None:
        st.header('Account Status')
        st.write(':green[Connected]')
        st.header('Account Balance')
        st.write(f'{user_balance} ETH')
    else:
        st.write('Please ensure your Mneumonic phrase is saved in a .env in this same directory.')
        st.write('Then restart this application.')


# Column that contains the functions to interact with smart contract
with functions_col:
    
    st.subheader('The :violet[Premier] ETH Lending and Borrowing Application')

    # Create the Tabs for streamlit
    lend_tab,borrow_tab,repay_tab,withdraw_tab,balances_tab = st.tabs(['Lend', 'Borrow', 'Repay', 'Withdraw', 'Balances'])

    # Creates Lend Tab
    with lend_tab:
        st.header('Lend')
        balance = user_balance
        st.write('Starting Balance:', f'{balance} ETH')    
        lend_amount = st.number_input('Enter the amount you want to lend (in ETH):')
        if lend_amount != 0:
            lend_interest_rate = st.write(f'{(lend_amount/treasury_balance * .5):.2}% Lending Interest' )
        else:
            lend_interest_rate = 0

        
        if st.button('Complete Lend',key='lend'):

            # sending loan to the TREASURY_ADDRESS
            send_transaction(w3=w3, account=user_account, to=TREASURY_ADDRESS, amount=lend_amount)
            balance = user_balance
            st.write(f'{lend_amount} has been deducted from your personal wallet.')    
            st.write(f'We owe you {lend_amount} + {(lend_amount/treasury_balance * .5):.2}% interst.')    
            st.write('New Balance:', balance)    

            # updates the balance of the TREASURY_ADDRESS
            st.write(f'Treasury balance now: {float(get_balance(w3=w3, address=TREASURY_ADDRESS))} ETH')

    # Creates Borrow Tab
    with borrow_tab:
        st.header('Borrow')
        balance = user_balance
        st.write('Balance:', balance)
        borrow_amount = st.number_input('Enter the amount you want to borrow (in ETH):')
        if borrow_amount != 0:
            borrow_interest_rate = st.write(f'{(borrow_amount/treasury_balance * 2):.2}% Borrow Interest')
        else:
            # Choose and insert default value for borrow_interest_rate
            borrow_interest_rate = 0
            

        if st.button('Complete Borrow',key='borrow'):

            # sending loan to the TREASURY_ADDRESS
            send_transaction(w3=w3, account=TREASURY_ACCOUNT_OBJECT, to=user_account.address, amount=borrow_amount)
            balance = user_balance
            st.write(f'{borrow_amount} has sent to your personal wallet.')    
            st.write(f'You owe us {borrow_amount} + {(borrow_amount/treasury_balance * 2):.2}% interst.')    
            st.write('New Balance:', balance)    

            # updates the balance of the TREASURY_ADDRESS
            st.write(f'Treasury balance now: {float(get_balance(w3=w3, address=TREASURY_ADDRESS))} ETH')

    # Creates Borrow Tab
    with repay_tab:
        st.header('Repay')
        st.write(f'Amount Owed: {borrow_balance/10**18} ETH')
        repay_amount = st.number_input('Enter amount to repay')
        if st.button('Submit',key='repay'):

            repay_amnt = 1
            # Converts repay amount into int and given wei value
            repay_amount_wei = Web3.toWei(repay_amnt*10**18, 'wei')
            repay = contract.functions.repay(repay_amount_wei).transact({'value': repay_amount_wei, 'from': w3.eth.accounts[0]})
            new_borrow_balance = contract.functions.borrowBalance(user_account).call()
            st.write(f'{repay_amount} has been repayed to the treasury for you debts.')    
            #  @TODO calculate and track interest_accrued    
            st.write(f'New Borrow Balance: {new_borrow_balance/10**18} ETH')
    
    with withdraw_tab:
        st.header('Withdraw')
        st.write(f'All Borrows must be paid before withdraw. Current Borrow Balance: {contract.functions.borrowBalance(user_account).call()/10**18} ETH')
        
        withdraw_amount = st.number_input('Amount to Withdraw')
        if st.button('Submit'):
            withdraw_amount_wei = Web3.toWei(withdraw_amount*10**18, 'wei')

            withdraw = contract.functions.withdraw(withdraw_amount_wei).transact({'from': w3.eth.accounts[0]})

            st.write(withdraw_balance = contract.functions.borrowBalance(user_account).call())

    #Creates Balances tab
    with balances_tab:
        st.header('Balances')
        if st.button('Get Balances'):
            balance = user_balance
            st.write(f' Account Balance: {balance} ETH')
            st.write(f'Borrow Balance: {borrow_balance/10**18} ETH')
            st.write(f'Lend Balance: {lend_balance/10**18} ETH')


        

