contract_state = {}
contract_details = {}
change_tax = {}
native_token_liquidity = {}

def get_contract_state(user_id):
    return contract_state.get(user_id)

def set_contract_state(user_id, state):
    contract_state[user_id] = state


def set_contract_detail(user_id, key, value):
    if user_id not in contract_details:
        contract_details[user_id] = {}
    contract_details[user_id][key] = value

def get_contract_details(user_id):
    return contract_details.get(user_id, {})

def delete_contract_details(user_id):
    if user_id in contract_details:
        del contract_details[user_id]

def set_change_tax(user_id, tax):
    change_tax[user_id] = tax

def get_change_tax(user_id):
    return change_tax.get(user_id)

def set_liq_amount(user_id, amount):
    native_token_liquidity[user_id] = amount

def get_liq_amount(user_id):
    return native_token_liquidity.get(user_id)