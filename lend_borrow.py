import web3
import streamlit as st
from dataclasses import dataclass
import yfinance as yf

treasury = 100 


st.title('ETH Borrow and Lend Application')



eth_price = yf.download(tickers='ETH-USD',period='1day', interval='1m',rounding=True).drop(columns=['Adj Close','Open','High','Low','Volume'])
eth_price['Percent Change']=eth_price['Close'].pct_change()


# liquidate signal
if (eth_price['Percent Change'][-1]) * 100 >= 5:
    st.write('Liquidate Risk High')
elif (eth_price['Percent Change'][-1]) * 100 <= 5:
    st.write('Liquidate Risk Low')

action = st.selectbox('Select an action', ['Lend', 'Borrow', 'Repay', 'Get Balance'])

if action == 'Lend':
    lend_amount = st.number_input('Enter the amount you want to lend (in ETH):')
    lend_interest_rate = st.write(f'{(lend_amount/treasury * .5):.2}% Lending Interest' )
    if st.button('Complete Lend'):
        treasury = treasury + lend_amount
        st.write(treasury)

if action == 'Borrow':
    borrow_amount = st.number_input('Enter the amount you want to borrow (in ETH):')
    borrow_interest_rate = st.write(f'{(borrow_amount/treasury * 2):.2}% Borrow Interest' )
    if st.button('Complete Borrow'):
        treasury = treasury - borrow_amount
        st.write(treasury)

if action == 'Repay':
    amount = st.number_input('Enter amount to repay')
    if st.button('Submit'):
        result = (amount)
        st.write('Repay successful. Transaction receipt:', result)

if action == 'Get Balance':
    user_address = st.text_input('Enter user address')
    if st.button('Submit'):
        result = (user_address)
        st.write('Balance:', result)
