from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ForceReply

from database.db import get_contracts, get_private_key, get_contract_details, verify_contract as verify, get_verification_status
from database.contract_deploy import get_contract_state, set_contract_state, get_change_tax, set_change_tax, get_liq_amount, set_liq_amount
from keyboards.menu import manage_contract_menu, select_contract, main_menu, contract_call_menu

from .utils import validate_input, display_contract_details
from requests import post
from utils.constants import verify_endpoint, add_liq_endpoint, edit_contract_endpoint

router = Router()
router.message.filter(F.chat.type == "private")

class ContractEditorStates(StatesGroup):
    setting_deploy = State() 
    setting_contract_edit = State() 
    add_excluded_wallet = State()
    change_tax_buy = State()
    change_tax_sell = State()
    add_liquidity_to_chain_asset = State()
    finalize_liquidity_pool = State()

async def manage_contracts_callback(callback: CallbackQuery, state: FSMContext):
    print("Manage Contract...")
    user_id = callback.from_user.id
    user_contracts = get_contracts(user_id)
    if user_contracts == None:
        await callback.message.answer(
            "You have no contracts to manage",
            reply_markup=main_menu(),
        )
        return
    
    contract_addresses = list(filter(None,user_contracts.split(',')))
    print("Contract Addresses: ", contract_addresses)
    contract_details = [get_contract_details(address) for address in contract_addresses]
    print("Contract Details: ", contract_details)
    contracts = [{'address': contract[0], 'symbol': contract[3]} for contract in contract_details]
    await callback.message.answer(
        "Please select the Contract Address of the token you want to manage",
        reply_markup=select_contract(contracts),
    )

async def select_contract_callback(callback: CallbackQuery, state: FSMContext):
    print("Selecting Contract...")
    user_id = callback.from_user.id
    contract_address = callback.data.split(':')[1]
    contract_details = get_contract_details(contract_address)
    print("Contract Details: ", contract_details)
    contract_info = None
    if contract_details == None:
        contract_info = "ERC21 Bot Token Builder"
    else:
        contract_info = display_contract_details(contract_details)
    await callback.message.answer("Generating Contract Details...")
    set_contract_state(user_id, contract_address)
    # Get contract details by instantiating an instance
    await callback.message.answer(
        contract_info,
        reply_markup=manage_contract_menu(contract_address),
        parse_mode='Markdown'
    )
    await state.set_state(ContractEditorStates.setting_contract_edit)

async def manage_contract_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    action = callback.data.split(':')[1]
    contract_address = get_contract_state(user_id)
    if contract_address == None:
        await callback.message.answer("There is an error proessing your request. Please try again later.")
        return
    if action == "verify":
        await verify_contract(callback, contract_address)
    elif action == "add_liquidity":
        await add_liquidity_chain_asset(callback, contract_address, state)
    elif action == "mod_contract":
        await callback.message.answer(
        "Modifying Contract...",
        reply_markup=contract_call_menu()
        )
    # Get contract details by instantiating an instance
    # set_contract_state(user_id, None)

async def verify_contract(callback: CallbackQuery, contract_address: str):
    # Verify a contract address
    verification_status = get_verification_status(contract_address)
    if verification_status == True:
        await callback.message.answer(
            "Contract is already verified!",
            reply_markup=manage_contract_menu(contract_address),
        )
        return
    response = post(verify_endpoint, json={'contract_address': contract_address})
    if response.ok == False:
        await callback.message.answer(
            "Contract Verification Failed!",
            reply_markup=manage_contract_menu(),
        )
        return
    verify(contract_address)
    await callback.message.answer(
        "Contract Verified!",
        reply_markup=manage_contract_menu(contract_address),
    )

async def add_liquidity_chain_asset(callback: CallbackQuery, contract_address: str, state: FSMContext):
    # Add Liquidity to a contract address
    contract_details = get_contract_details(contract_address)
    if contract_details == None:
        await callback.message.answer(
            "There is an error processing your request. Please try again later.",
            reply_markup=manage_contract_menu(),
        )
        return
    chain_token_name = contract_details[1]
    await callback.message.answer(
            f"Enter amount of {chain_token_name} to add to liquidity pool",
            reply_markup=ForceReply(selective=True),
        )
    await state.set_state(ContractEditorStates.add_liquidity_to_chain_asset)

async def process_add_liquidity_chain_asset(message: Message, state: FSMContext):
    await message.answer("Processing Liquidity Pool update...")
    text = message.text.strip()
    user_id = message.from_user.id
    clean_text = validate_input('decimals', text)
    if clean_text[0] == False:
        await message.answer(
            f"Invalid input, please try again",
            reply_markup=manage_contract_menu()
        )
        # await state.set_data("manage:add_liquidity")
        return
    contract_address = get_contract_state(user_id)
    if contract_address == None:
        await message.answer("There is an error processing your request. Please try again later.")
        return
    token_name = get_contract_details(contract_address)
    set_liq_amount(user_id, clean_text[1])
    await message.answer(
            f"Enter amount of {token_name[2]} tokens to add to the liquidity pool",
            reply_markup=ForceReply(selective=True),
        )
    await state.set_state(ContractEditorStates.finalize_liquidity_pool)

async def process_add_liquidity(message: Message, state: FSMContext):
    await message.answer("Processing Add Token Liquidity...")
    text = message.text.strip()
    user_id = message.from_user.id
    private_key = get_private_key(user_id)
    contract_address = get_contract_state(user_id)
    clean_text = validate_input('decimals', text)
    native_amount = get_liq_amount(user_id)
    if clean_text[0] == False:
        print("Invalid input")
        await message.answer(
            "Invalid input for Token amount, please try again"
        )
        await state.set_state(ContractEditorStates.add_liquidity_to_chain_asset)
        return
    if contract_address == None:
        await message.answer("There is an error processing your request. Please try again later.")
        return
    if native_amount == None:
        await message.answer("There was an error processing native token input. Please try again.")
        return
    liquidity_amount = {'eth_amount':native_amount,'token_amount': clean_text[1]}
    request_object = {'private_key': f"0x{private_key}", 'contract_address': contract_address, 'liquidity_amount': liquidity_amount}
    response = post(add_liq_endpoint, json=request_object)
    if response.ok == False:
        await message.answer("Liquidity function was unsuccessful in invocation. Please try again")
        await state.set_state(ContractEditorStates.add_liquidity_to_chain_asset)
        return
    set_contract_state(user_id, None)
    set_liq_amount(user_id, None)
    await message.answer("Buy and Sell taxes has been updated", reply_markup=manage_contract_menu())

async def call_contract_callback(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(':')[1]
    if action == 'addExcludedWallet':
        await callback.message.answer(
            "Enter the wallet address you want to exclude from tax",
            reply_markup=ForceReply(selective=True),
        )
        await state.set_state(ContractEditorStates.add_excluded_wallet)
    elif action == 'changeTax':
        await callback.message.answer(
            "Enter the new buy tax rate",
            reply_markup=ForceReply(selective=True),
        )
        await state.set_state(ContractEditorStates.change_tax_buy)
    else:
        await callback.message.answer(
            "Processing Contract call..."
        )
        await call_edit_endpont(callback.message, action, {}, user_id=
    callback.from_user.id)
        
    # await callback.message.answer("Contract has been modified")

async def process_add_excluded_wallet_callback(message: Message, state: FSMContext):
    await message.answer("Processing Wallet Exclusion update...")
    text = message.text.strip()
    user_id = message.from_user.id
    clean_text = validate_input('fee_recipient', text)
    if clean_text[0] == False:
        print("Invalid input")
        await message.answer(
            f"Invalid input for wallet to be excluded, please try again",
            reply_markup=contract_call_menu()
        )
        return
    params = {'wallet': clean_text[1]}
    await call_edit_endpont(message, 'addExcludedWallet', params, user_id)

async def process_tax_buy(message: Message, state: FSMContext):
    await message.answer("Processing Buy Tax update...")
    text = message.text.strip()
    clean_text = validate_input('buy_tax', text)
    if clean_text[0] == False:
        await message.answer(
            f"Invalid input for buy tax, please try again",
            reply_markup=contract_call_menu()
        )
        return
    set_change_tax(user_id=message.from_user.id, tax=clean_text[1])
    await message.answer(
            "Enter the new sell tax rate",
            reply_markup=ForceReply(selective=True),
        )
    await state.set_state(ContractEditorStates.change_tax_sell)

async def process_change_tax(message: Message, state: FSMContext):
    await message.answer("Processing Sell Tax update...")
    text = message.text.strip()
    user_id = message.from_user.id
    clean_text = validate_input('buy_tax', text)
    if clean_text[0] == False:
        print("Invalid input")
        await message.answer(
            f"Invalid input for sell tax, please try again",
            reply_markup=contract_call_menu()
        )
        return
    buy_tax = get_change_tax(user_id)
    tax = {'newBuyTax': buy_tax, 'newSellTax': clean_text[1]}
    print('Edit Tax from state storage: ', tax)
    set_change_tax(user_id, None)
    await call_edit_endpont(message, 'changeTax', tax, user_id)

async def call_edit_endpont(message: Message, key: str, params: dict, user_id: int):
    private_key = get_private_key(user_id)
    contract_address = get_contract_state(user_id)
    if contract_address == None:
        await message.answer("There is an error processing your request. Please try again later.")
        return
    request_object = {'key': key, 'private_key': f'0x{private_key}', 'contract_address': contract_address, 'params': params}
    response = post(edit_contract_endpoint, json=request_object)
    if response.ok == False:
        await message.answer("Contract call was unsuccessful and has been reverted", reply_markup=contract_call_menu())
    await message.answer("Contract call successfully executed", reply_markup=contract_call_menu())