import streamlit as st
from dataclasses import dataclass
import yfinance as yf
from crypto_wallet import generate_account, get_balance, send_transaction, access_treasury_account
from web3 import Web3
import time

# creates a Web3 instance of the Ganache network on local machine
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

# """TREASURY - Redefine  by connecting to Ganache"""
# for testing: choose a wallet addres that is part of Ganache, copy an paste into TREASURY_ADDRESS
TREASURY_ADDRESS = "0x5F36AF892d95E477D9ae6E9Cc59aaAAEdeAa8B58"
# for testing: copy and paste the private key into TREASURY_KEY
TREASURY_KEY = "0056aa03c6c079604d0d9015f477c9c30cddec1a1b5ff121f3fce78db99fee2d"
TREASURY_ACCOUNT_OBJECT = access_treasury_account(TREASURY_KEY)
treasury_balance = float(get_balance(w3=w3, address=TREASURY_ADDRESS))


st.title(':green[---------------]:blue[$PyBo$]:green[Lend]:blue[----------------]')


eth_price = yf.download(tickers='ETH-USD',period='1day', interval='1m',rounding=True).drop(columns=['Adj Close','Open','High','Low','Volume'])
eth_price['Percent Change']=eth_price['Close'].pct_change()
percent_change=eth_price['Percent Change'].mean()*100

col1, col2, col3 = st.columns([1,4.75,1])

with col1:
    st.write(f"Treasury is: {treasury_balance}")
    # liquidate signal
    if percent_change >= 1:
        #st.write(f'Average Price Change :red[{percent_change:.3f}]%')
        st.write('Liquidate Risk :red[High]')
    elif percent_change <= 1:
        #st.write(f'Average Price Change :green[{percent_change:.3f}]%')
        st.write('Liquidate Risk :green[Low]')



with col3:
# Loads account credentials
    user_account = generate_account()
    if user_account != None:
        st.write("Your account is :green[Connected].")
        st.write(f"Your balance is: {get_balance(w3=w3, address=user_account.address)}ETH.")
    else:
        st.write("Please ensure your Mneumonic phrase is saved in a .env in this same directory.")
        st.write("Then restart this application.")

with col2:
    
    st.subheader('The :violet[Premier] ETH Lending and Borrowing Application')

    # Create the Tabs for streamlit
    lend_tab,borrow_tab,repay_tab, balance_tab = st.tabs(['Lend', 'Borrow', 'Repay', 'Get Balance'])

    # Creates Lend Tab
    with lend_tab:
        st.header('Lend')
        balance = get_balance(w3,user_account.address)
        st.write('Starting Balance:', balance)    
        lend_amount = st.number_input('Enter the amount you want to lend (in ETH):')
        if lend_amount != 0:
            lend_interest_rate = st.write(f'{(lend_amount/treasury_balance * .5):.2}% Lending Interest' )
        else:
            lend_interest_rate = 0

        
        if st.button('Complete Lend',key='lend'):

            # sending loan to the TREASURY_ADDRESS
            send_transaction(w3=w3, account=user_account, to=TREASURY_ADDRESS, amount=lend_amount)
            balance = get_balance(w3,user_account.address)
            st.write(f'{lend_amount} has been deducted from your personal wallet.')    
            st.write(f'We owe you {lend_amount} + {(lend_amount/treasury_balance * .5):.2}% interst.')    
            st.write('New Balance:', balance)    

            # updates the balance of the TREASURY_ADDRESS
            st.write(f"Treasury balance now: {float(get_balance(w3=w3, address=TREASURY_ADDRESS))} ETH")

    # Creates Borrow Tab
    with borrow_tab:
        st.header('Borrow')
        balance = get_balance(w3,user_account.address)
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
            balance = get_balance(w3,user_account.address)
            st.write(f'{borrow_amount} has sent to your personal wallet.')    
            st.write(f'You owe us {borrow_amount} + {(borrow_amount/treasury_balance * 2):.2}% interst.')    
            st.write('New Balance:', balance)    

            # updates the balance of the TREASURY_ADDRESS
            st.write(f"Treasury balance now: {float(get_balance(w3=w3, address=TREASURY_ADDRESS))} ETH")

    # Creates Borrow Tab
    with repay_tab:
        st.header('Repay')
        balance = get_balance(w3,user_account.address)
        st.write('Amount Owed', balance)
        repay_amount = st.number_input('Enter amount to repay')
        if st.button('Submit',key='repay'):

            send_transaction(w3=w3, account=user_account, to=TREASURY_ADDRESS, amount=repay_amount)
            
            st.write(f'{repay_amount} has been repayed to the treasury for you debts.')    
            #  @TODO calculate and track interest_accrued
            #  @TODO determine a way to make brrow_amount a global varaible, line 120 does not function becauce borrow_amount as defined in line 75 does not carry beyond if statement
            # st.write(f'You owe us {borrow_amount - repay_amount} + interest accrued.')    
            st.write('New Balance:', balance)    

            # updates the balance of the TREASURY_ADDRESS
            st.write(f"Treasury balance now: {float(get_balance(w3=w3, address=TREASURY_ADDRESS))} ETH")

    #Creates Balance tab
    with balance_tab:
        st.header('Get Balance')
        balance = get_balance(w3,user_account.address)
        if st.write('Balance', balance):

            """Note: Without a Smart Contract, this would need to reference a database or private ledger to properly function."""
            # debt_or_credit = get_balance(w3,debt_or_credit_account)
            # st.write('Balance:', debt_or_credit)

        

