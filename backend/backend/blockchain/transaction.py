from web3 import Web3
from eth_abi import encode

def encode_transaction_data(function_signature, abi, parameters):
    w3 = Web3()

    function_selector = w3.keccak(text=function_signature)[:4]
    encoded_parameters = encode(abi, parameters)

    encoded_function_call = function_selector + encoded_parameters

    return w3.to_hex(encoded_function_call)