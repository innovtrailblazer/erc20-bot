import secrets
from web3 import Web3
from .config import RPC_URL, BOT_CONTRACT
# from .abi import abi_manager

w3 = Web3(Web3.HTTPProvider(RPC_URL))
# BOT_CONTRACT = Web3.to_checksum_address(BOT_CONTRACT)

# contract = w3.eth.contract(address=BOT_CONTRACT, abi=abi_manager.get_abi('FriendtechSharesV1'))

def is_valid_eth_private_key(pk: str):
    pk = pk[2:] if pk.startswith('0x') else pk
    if len(pk) == 64 and pk.isalnum():
        return pk  
    
    return False  

def generate_eth_private_key():
    # A private key is a 256-bit number, which can be represented as a 32-byte hexadecimal
    max_hex_value = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140 
    private_key_hex = secrets.randbelow(max_hex_value)  
    
    # Converting the number to a hexadecimal string and ensuring it has a length of 64 characters
    return hex(private_key_hex)[2:].zfill(64)

def get_eth_balances(wallet_addresses):
    balances = {}
    
    for wallet_address in wallet_addresses:
        balance_wei = w3.eth.get_balance(wallet_address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        balances[wallet_address] = balance_eth
        
    return balances