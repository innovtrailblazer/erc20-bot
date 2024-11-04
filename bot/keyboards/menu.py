import re
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import Optional

from database.keyboard_state import get_keyboard_state, generate_uuid_from_pKey
from database.db import get_verification_status
from utils.constants import supported_chains
from utils.blockchain import w3
from utils.formatting import truncate_address



router = Router()

class MenuFactory(CallbackData, prefix="trade"):
    action: str
    process: Optional[str] = None
    subject: Optional[str] = None

def main_menu():
    markup = InlineKeyboardBuilder()
    markup.button(text="🔧 Manage Wallets", callback_data="main_wallet")
    markup.button(text="🏗️ Deployment Menu", callback_data="contract_create")
    markup.button(text="📝 Deployed Tokens", callback_data="contract_manage")
    markup.adjust(1,2)
    return markup.as_markup()

def generate_menu():
    markup = InlineKeyboardBuilder()
    markup.button(text="💼 Create", callback_data="wallet_create")
    markup.button(text="📤 Import", callback_data="wallet_import")
    markup.button(text="🗑️ Delete", callback_data="wallet_delete")
    markup.button(text="🏗️ Deployments", callback_data="wallet_deployments")

    markup.adjust(2, 2)
    return markup.as_markup()

def deployer_main_menu():
    markup = InlineKeyboardBuilder()
    markup.button(text="🚀 Deploy Contract", callback_data="contract_create")
    markup.button(text="📝 Manage Contracts", callback_data="contract_manage")
    markup.adjust(2)
    return markup.as_markup()

def deployer_menu(user_id):
    current_state = get_keyboard_state(user_id)
    if current_state:
        return current_state
    markup = InlineKeyboardBuilder()
    markup.button(text="⛓️ Chain", callback_data="deployer:chain")
    markup.button(text="📛 Token Name", callback_data="deployer:token_name")
    markup.button(text="💲 Token Symbol", callback_data="deployer:token_symbol")
    markup.button(text="🔢 Token Decimals", callback_data="deployer:token_decimal")
    markup.button(text="📊 Token Supply", callback_data="deployer:token_supply")
    markup.button(text="📈 Buy Tax", callback_data="deployer:buy_tax")
    markup.button(text="📉 Sell Tax", callback_data="deployer:sell_tax")
    markup.button(text="🎢 Max Txn Amount", callback_data="deployer:max_txn_amount")
    markup.button(text="💎 Fee Recipient", callback_data="deployer:fee_recipient")
    markup.button(text="📤 Deploy", callback_data="deployer:deploy")
    markup.adjust(1,2,2,2,2,1)
    return markup.as_markup()

def select_chain():
    markup = InlineKeyboardBuilder()
    for chain in supported_chains:
        markup.button(text=chain['name'], callback_data=f"chain_select:{chain['chain']}")
    markup.adjust(1)
    return markup.as_markup()

def deploy_menu():
    markup = InlineKeyboardBuilder()
    markup.button(text="✔️ Proceed", callback_data="deploy:proceed")
    markup.button(text="✖️ Cancel", callback_data="deploy:cancel")
    markup.adjust(2)
    return markup.as_markup()

def select_contract(contracts: list[dict]):
    markup = InlineKeyboardBuilder()
    for contract in contracts:
        text = f"{contract['symbol']}: {truncate_address(contract['address'])}"
        markup.button(text=text, callback_data=f"contract_select:{contract['address']}")
    markup.adjust(2)
    return markup.as_markup()

def select_wallet(private_keys: list[str], action: str = 'delete'):
    markup = InlineKeyboardBuilder()
    markup.button(text="💼 Create", callback_data="wallet_create")
    markup.button(text="📤 Import", callback_data="wallet_import")
    for private_key in private_keys:
        wallet_address = w3.eth.account.from_key(private_key).address
        address = truncate_address(wallet_address)
        uuid = generate_uuid_from_pKey(private_key)
        markup.button(text=address, callback_data=f"wallet_select:{uuid}:{action}")
    markup.adjust(2)
    return markup.as_markup()

def manage_contract_menu(contract_address: str):
    markup = InlineKeyboardBuilder()
    verification_status = get_verification_status(contract_address)
    text = "Verified ✅" if verification_status else "Verify Contract"
    markup.button(text=text, callback_data="manage:verify")
    markup.button(text="Add Liquidity", callback_data="manage:add_liquidity")
    markup.button(text="Modify Contract", callback_data="manage:mod_contract")
    markup.adjust(2,1)
    return markup.as_markup()

def contract_call_menu():
    markup = InlineKeyboardBuilder()
    markup.button(text="📈 Add Excluded Wallet", callback_data="contract_call:addExcludedWallet")
    markup.button(text="📉 Change Tax", callback_data="contract_call:changeTax")
    markup.button(text="🎢 Open Trading", callback_data="contract_call:openTrading")
    markup.button(text="💎 Remove Limits", callback_data="contract_call:removeLimits")
    markup.adjust(2,2)
    return markup.as_markup()

def set_main_wallet_menu(pKey):
    markup = InlineKeyboardBuilder()
    uuid = generate_uuid_from_pKey(pKey)
    markup.button(text="🔑 Set as Main Wallet", callback_data=f"set_main_wallet:{uuid}")
    markup.adjust(1)
    return markup.as_markup()

def deployer_wallet_menu(contracts: list[dict], pKey: str, is_main: bool):
    markup = InlineKeyboardBuilder()
    uuid = generate_uuid_from_pKey(pKey)
    if is_main == False:
        markup.button(text="🔑 Set as Main Wallet", callback_data=f"set_main_wallet:{uuid}")
    for contract in contracts:
        text = f"{contract['symbol']}: {truncate_address(contract['address'])}"
        markup.button(text=text, callback_data=f"contract_select:{contract['address']}")
    markup.adjust(1, len(contracts) // 2 + len(contracts) % 2)
    return markup.as_markup()