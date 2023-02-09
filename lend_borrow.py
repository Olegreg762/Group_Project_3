import web3
import streamlit as st
from dataclasses import dataclass

def main():
    treasury = 100 
    st.title('ETH Borrow and Lend Application')

    # Lender Section
    st.header('Lender')
    lend_amount = st.number_input('Enter the amount you want to lend (in ETH):')
    lend_interest_rate = st.write(f'{(lend_amount/treasury * .5):.2}% Lending Interest' )
    if st.button('Complete Lend'):
        treasury = treasury + lend_amount
        st.write(treasury)
    
    

    
    # Borrower Section
    st.header('Borrower')
    borrow_amount = st.number_input('Enter the amount you want to borrow (in ETH):')
    borrow_interest_rate = st.write(f'{(borrow_amount/treasury * 2):.2}% Borrow Interest' )
    if st.button('Complete Borrow'):
        treasury = treasury - borrow_amount
        st.write(treasury)



 
main()
