import os
import time
from web3 import Web3
from eth_abi import encode

def encode_transaction_data(function_signature, abi, parameters):
    w3 = Web3()

    function_selector = w3.keccak(text=function_signature)[:4]
    encoded_parameters = encode(abi, parameters)

    encoded_function_call = function_selector + encoded_parameters

    return w3.to_hex(encoded_function_call)

def wait_for_transaction_mining(tx_hash, poll_interval=10):
    w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))

    while True:
        try:
            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
            if tx_receipt is not None:
                return tx_receipt
            else:
                print("Transaction not mined yet, waiting...")
                time.sleep(poll_interval)
        except Exception as e:
            print(f"{e}")
            time.sleep(poll_interval)

def wait_for_confirmations(tx_hash, confirmations=5, poll_interval=10):
    w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))

    tx_receipt = wait_for_transaction_mining(tx_hash)

    while True:
        current_block = w3.eth.block_number
        confirmations_count = current_block - tx_receipt.blockNumber

        if confirmations_count >= confirmations:
            return tx_receipt
        else:
            print(f"Transaction has {confirmations_count} confirmations, waiting for more...")
            time.sleep(poll_interval)
