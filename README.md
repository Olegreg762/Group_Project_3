# PyBo Lend - A DeFi App Built Using Solidity and Python

## Table of Contents

1. [Project Concept](#Project-Concept)
1. [Features](#Features)
1. [Test Cases](#Test-Cases)
1. [Code Dependencies](#Project-Team)
1. [Contribution Guidelines](#Contribution-Guidelines)
1. [Contact](#Contact)
1. [License](#License)

## Project Concept
The goal of this project is to create a decentralized lending application utilizing a solidity smart contract  and a user interface coded in Python.  The core  features of the solidity smart contract are lending, borrowing, repaying debts,  and withdrawing funds. Since the smart contract is coded in solidity,  the asset being lent and borrowed is Ether from the ethereum test network.  Although the test cases compiled for this project do not involve real money,  it functions as a proof of concept  for zero custody lending application that could be deployed on the Ethereum network.


[Repo Link](https://github.com/Olegreg762/Group_Project_3) <br>
![Repo Image](Images/Screenshot1_Landing.png)

## Features

### Lending
Lending functionality is coded across two core files: `pylend.sol`, `lend_borrow.py`. The initial implementation is in the smart contract:

```solidity
function lend() public payable{
    require(msg.value > 0, "Amount must be greater than zero");
    contractBalance += msg.value;
    lendBalance += msg.value;
    //Broadcast the Lend
    emit Lend(msg.sender, msg.value);
```

After deploying an instance of the contract, a user is able to submit ETH to the contact in the form of a loan, the contractBalance gets updated with the value sent, then the lendBalance is updated, and finally the Lending event is broadcast to the blockchain.

The user's interaction with the contract occurs on lend_borrow.py:


```python
if st.button('Complete Lend',key='lend'):

    # sending loan to the TREASURY_ADDRESS
    lend_amount_wei = Web3.toWei(lend_amount*10**18, 'wei')
    lend_activity = contract.functions.lend().transact({'value': lend_amount_wei, 'from': w3.eth.accounts[0]})

    balance = user_balance
    st.write(f'{lend_amount} has been deducted from your personal wallet.')    
    st.write(f'We owe you {lend_amount} + {(lend_amount/treasury_balance * .5):.2}% interest.')
    st.write('New Balance:', balance)    

    # updates the balance of the TREASURY_ADDRESS

    updated_treasury_balance = w3.eth.get_balance(os.getenv('SMART_CONTRACT_ADDRESS'))/10**18
    st.write(f'The new treasury balance is: {updated_treasury_balance} ETH')
```

If the Lend button is clicked, the amount input by the user is converted to wei. Then the lend transaction from the solidity contract is saved to the variable `lend_activity`. The users balance is updated to the user interface. The last two lines of code, save the new contract balance to a variable, then display that balance to the UI.



### Borrowing
Borrowing functionality is coded across two core files: `pylend.sol`, `lend_borrow.py`. The initial implementation is in the smart contract:

```solidity
function borrow(uint256 amount) public {
    require(amount > 0, "Amount must be greater than zero");
    require(lendBalance >= amount, "Borrow Amount must be less than Amount Lended");
    //Limits Borrow amount to 80% of the amount lended
    require(borrowBalance[msg.sender].add(amount) <= lendBalance.mul(8).div(10), "Borrow Amount exceeds 80% of Lend Amount");

    msg.sender.transfer(amount);
    borrowBalance[msg.sender] += amount;
    contractBalance -= amount;
    //Broadcast the Borrow
    emit Borrow(msg.sender, amount);
```

Before a borrow transaction can be executed certain requirements are verified. Including limiting what a user can borrow to 80% of the total amount they have already loaned. The amount gets transferred to the user, their contract balance is updated (and a corresponding amount from the contract balance is reduced), and the event is broadcast to the network

### Repay
Repay functionality is coded across two core files: `pylend.sol`, `lend_borrow.py`. The initial implementation is in the smart contract:

```solidity
function repay(uint256 amount) public payable {
    amount = msg.value;
    require(amount > 0, "Amount must be greater than zero");
    require(amount <= borrowBalance[msg.sender], "Repay must be less than amount borrrowed");
    require(borrowBalance[msg.sender] >= 0, "No Borrow Amount to Repay");

    borrowBalance[msg.sender] -= amount;
    contractBalance += amount;
    //Broadcast the Repay amount
```

Before a user can repay their loan, certain requirements are verified. Their borrow balance is then reduced by the amount repaid (and the contractBalance increased accordingly).


### Withdraw Balance
Withdraw functionality is coded across two core files: `pylend.sol`, `lend_borrow.py`. The initial implementation is in the smart contract:

```solidity
function withdraw (uint256 amount) public{
    require(amount > 0, "Amount must be greater than zero");
    require(lendBalance >= amount, "No Funds to Withdraw");
    require(borrowBalance[msg.sender] <= amount, "All Borrowed Amounts must be Repayed before Withdrawing");
    lendBalance -= amount;
    contractBalance -= amount;
    msg.sender.transfer(amount);

    emit Withdraw(msg.sender, amount);
```

Before a user can withdraw, certain requirements are verified. Then the lendBalance and contractBalance and both reduced by the amount withdrawn. The transfer to the user is executed, and the event is broadcast to the blockchain. 

### Interest Rate Calculation
Interest functionality is coded in `Interest_rate.py`, imported into `lend_borrow.py`, then then sent over to the `pylend.sol` smart contract.

## Test Cases
- Lending successful execution
- ![Lending](./Images/-.png)
- Interest earned over time
- ![Interest](./Images/-.png)
- Borrowing successful exection
- ![Borrowing](./Images/-.png)
- Interest accrued is not eaten up by gas fees
- ![Interest](./Images/-.png)


## Code and Dependencies
This code is to be run on 
`Python 3.7.13`

The following Python Libraries were also imported and used

### Imports
```python
import pandas as pd
import numpy as np
import os
import requests
from dotenv import load_dotenv
from bip44 import Wallet
from web3 import Account
from web3 import middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from mnemonic import Mnemonic
from lend_borrow import load_contract
import streamlit as st
from dataclasses import dataclass
import yfinance as yf
from web3 import Web3
import time
from pathlib import Path
import json
```

## Instructions

1. Clone the repository to your local device 
2. Download and run an instance of the Ganache as well
3. Open up remix.ethereum.org, paste the contents of the `pylend.sol` file into a new .sol file on Remix
4. After compiling the code, copy the ABI file into the `pylend_abi.json` file, and save
5. Deploy the contract. Copy the contract address, and paste into a .env file that is in the same directory as this repository on your local machine. Ensure this is saved as a string to the variable `SMART_CONTRACT_ADDRESS`
6. Run the `lend_borrow.py` file by calling the command `streamlit run lend_borrow.py`


## Project Team

[Ben Eilers](https://github.com/bweilers) <br>
[Kyle Hagan](https://github.com/hagankj) <br>
[Jose Olasa](https://github.com/joseolasa) <br>
[Greg Stevenson](https://github.com/Olegreg762) <br>

## Contribution Guidelines:

```
Feel free to contribute to this repo by creating issues or sending an email to any of the contributors in the list below.
```

## Contact

<details>
    <summary>Contact</summary>
    ben.eilers@gmail.com <br>
    kylejhagan@gmail.com <br>
    joseolasa@gmail.com <br>
    playb3yond40gb@gmail.com <br>

</details>

## License

#### Distributed under the MIT License. 
