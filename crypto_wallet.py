# Cryptocurrency Wallet
################################################################################

# Imports
import os
import requests
from dotenv import load_dotenv

load_dotenv()
from bip44 import Wallet
from web3 import Account
from web3 import middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from mnemonic import Mnemonic


################################################################################
# Wallet functionality


def generate_account():
    """Create a digital wallet and Ethereum account from a mnemonic seed phrase."""
    # Fetch mnemonic from environment variable.
    mnemonic = os.getenv("MNEMONIC")

    # """Check with team members if our app should have the functionality to generate new wallet credentials"""
    # Use an if-statement to check if the mnemonic variable is None and generates a mnemoic 
    # if mnemonic is None:
    #     mnemo = Mnemonic("english")
    #     mnemonic = mnemo.generate(strength=128)

    # Create Wallet Object
    wallet = Wallet(mnemonic)

    # Derive Ethereum Private Key
    private, public = wallet.derive_account("eth")

    # Convert private key into an Ethereum account
    account = Account.privateKeyToAccount(private)

    return account


def get_balance(w3, address):
    """Using an Ethereum account address access the balance of Ether"""
    # Get balance of address in Wei
    wei_balance = w3.eth.get_balance(address)

    # Convert Wei value to ether
    ether = w3.fromWei(wei_balance, "ether")

    # Return the value in ether
    return ether


"""Original"""
def send_transaction(w3, account, to, amount):
    """Send an authorized transaction to the Ganache blockchain."""
    # Set gas price strategy
    w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

    # Convert eth amount to Wei
    value = w3.toWei(amount, "ether")

    # Calculate gas estimate
    gasEstimate = w3.eth.estimateGas(
        # for testing
        {"to": to, "from": account.address, "value": value}
    )

    # Construct a raw transaction
    raw_tx = {
        "to": to,
        "from": account.address,
        "value": value,
        "gas": gasEstimate,
        "gasPrice": 0,
        "nonce": w3.eth.getTransactionCount(account.address),
    }

    # Sign the raw transaction with ethereum account, goes onto the blockchain
    signed_tx = account.signTransaction(raw_tx)

    # Send the signed transactions
    return w3.eth.sendRawTransaction(signed_tx.rawTransaction)


"""Access the Test Treasury Account -- For demo purposes"""
def access_treasury_account(private_key):
    account = Account.privateKeyToAccount(private_key)
    return account

