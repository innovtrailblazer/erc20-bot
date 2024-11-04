# handlers.py
from database.contract_deploy import get_contract_details

def update_contract_message(user_id):
    details = get_contract_details(user_id)
    message_text = f"""
ERC21 Token Builder
Chain: {details.get('chain', '----')} 
Token Name: {details.get('token_name', '----')}
Token Symbol: {details.get('token_symbol', '----')}
Token Decimals: {details.get('token_decimal', '----')}
Token Supply: {details.get('token_supply', '----')}
Buy Tax: {details.get('buy_tax') + '%' if details.get('buy_tax') else '----'}
Sell Tax: {details.get('sell_tax') + '%' if details.get('sell_tax') else '----'}
Max Txn Amount: {details.get('max_txn_amount', '----')}
Fee Recipient: {details.get('fee_recipient', '----')}
"""
    return message_text

def display_contract_details(contract_details):
    message_text = f"""
ERC21 Token Builder
Chain: {contract_details[1]}
Token Name: {contract_details[2]}
Token Symbol: {contract_details[3]}
"""
    return message_text

def format_deployed_tokens_message(token_data):
    message_lines = []
    for address, chain, coin_name, coin_symbol, _, balance in token_data:
        line = f"Address: `{address}`\nChain: {chain}\nToken: {coin_name} ({coin_symbol})"
        message_lines.append(line)
    return "\n\n".join(message_lines)

def validate_input(task, text):
    match task:
        case "chain":
            valid = text in ["BSC", "ETH", "MATIC"]
            return [valid, text]
        case "token_name":
            valid = len(text) > 0
            title = text.title()
            return [valid, title]
        case "token_symbol":
            valid = len(text) > 0 and ' ' not in text
            upper = text.upper()
            return [valid, upper]
        case "token_decimal":
            valid = text.isnumeric()
            return [valid, text]
        case "token_supply":
            valid = text.isnumeric()
            return [valid, text]
        case "buy_tax":
            valid = text.isnumeric()
            return [valid, text]
        case "sell_tax":
            valid = text.isnumeric()
            return [valid, text]
        case "max_txn_amount":
            valid = text.isnumeric()
            return [valid, text]
        case "fee_recipient":
            valid = len(text) == 42
            return [valid, text]
        case 'decimals':
            try:
                float(text)
                return [True, text]
            except:
                return [False, text]
        
def validate_contract_details(contract_details):
    keys_to_check = ['chain', 'token_name', 'token_symbol', 'token_decimal', 'token_supply', 'buy_tax', 'sell_tax', 'max_txn_amount', 'fee_recipient']
    all_keys_present = all(key in contract_details for key in keys_to_check)
    all_values_valid = all(validate_input(key, contract_details[key])[0] for key in keys_to_check)
    return all_keys_present and all_values_valid
