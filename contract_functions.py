import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv


'''
def load_contract():
    global w3
    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
    
    # Load Art Gallery ABI
    with open(Path('pylend_abi.json')) as f:
        certificate_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=certificate_abi
    )
    # Return the contract from the function
    return contract


# Load the contract
contract = load_contract()




def lend(amount):
    tx_hash = contract.functions.lend().transact({'value': amount})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt.status

def borrow(amount):
    tx_hash = contract.functions.borrow(amount).transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt.status

def repay(amount):
    tx_hash = contract.functions.repay(amount).transact({'value': amount})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt.status

def withdraw(amount):
    tx_hash = contract.functions.withdraw(amount).transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt.status

def function(action, amount=None):
    if action == 'lend':
        tx_hash = contract.functions.lend().transact({'value': amount})
    elif action == 'borrow':
        tx_hash = contract.functions.borrow(amount).transact()
    elif action == 'repay':
        tx_hash = contract.functions.repay(amount).transact({'value': amount})
    elif action == 'withdraw':
        tx_hash = contract.functions.withdraw(amount).transact()
    else:
        raise ValueError('Invalid action')

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt.status

#lend_balance = contract.functions.lendBalance().call()
#borrow_balance = contract.functions.borrowBalance(web3.eth.defaultAccount).call()
'''