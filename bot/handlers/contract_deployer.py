from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State

from requests import post
from utils.constants import deploy_endpoint

from database.db import add_contract_details, add_contract, get_private_key
from database.keyboard_state import set_keyboard_state, delete_keyboard_state
from database.contract_deploy import get_contract_details, set_contract_detail, delete_contract_details
from keyboards.menu import deployer_menu, select_chain, deploy_menu, main_menu

from .utils import update_contract_message, validate_input,  validate_contract_details

router = Router()
router.message.filter(F.chat.type == "private")

class DeployerStates(StatesGroup):
    setting_deploy = State() 
    setting_contract_edit = State() 

from aiogram.types import ForceReply

async def deploy_contract_callback(callback: CallbackQuery, state: FSMContext):
    print("Initializing Builder...")

    user_id = callback.from_user.id
    preload_message = await callback.message.answer("Initializing Builder...")
    message = update_contract_message(user_id)
    await preload_message.edit_text(
        message,
        reply_markup=deployer_menu(user_id),
        parse_mode='Markdown'
    )

async def deployer_contract_handler_callback(callback: CallbackQuery, state: FSMContext):
    print("Editing Contract deployment data...")
    user_id = callback.from_user.id
    task = callback.data.split(':')[1]
    if task == "chain":
        keyboard = select_chain()
        await callback.message.answer("Please select a chain", reply_markup=keyboard)
        return
    if task == "deploy":
        keyboard = deploy_menu()
        contract_message = update_contract_message(user_id)
        await callback.message.answer(
            f"Please confirm your contract details\n{contract_message}",
            reply_markup=keyboard)
        return
    await callback.message.answer(
        f"Please enter a value for {task}",
        reply_markup=ForceReply(selective=True),
    )
    await state.set_state(DeployerStates.setting_deploy)

async def process_deployer_contract_handler_callback(message: Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.reply_to_message.text.split(' ')[-1].strip()
    text = message.text.strip()
    keyboard = deployer_menu(user_id)
    clean_text = validate_input(task, text)
    print("Processing Contract...", task, text, clean_text)
    if clean_text[0] == False:
        print("Invalid input")
        await message.answer(
            f"Invalid input for {task}, please try again",
            reply_markup=keyboard
        )
        return
    if keyboard and keyboard.inline_keyboard:
        for keyboard_row in keyboard.inline_keyboard:
            for keyboard_button in keyboard_row:
                if keyboard_button.callback_data == f"deployer:{task}":
                    if "✅" not in keyboard_button.text:
                        keyboard_button.text += " ✅"
    set_keyboard_state(user_id, keyboard)
    set_contract_detail(user_id, task, clean_text[1])
    contract_message = update_contract_message(user_id)

    await message.answer(contract_message, reply_markup=keyboard, parse_mode='Markdown')
    
async def chain_select_callback(callback: CallbackQuery, state: FSMContext):
    print("Selecting Chain...")
    await callback.message.answer('Selecting Chain...')
    user_id = callback.from_user.id
    chain = callback.data.split(':')[1]
    keyboard = deployer_menu(user_id)
    for keyboard_row in keyboard.inline_keyboard:
        for keyboard_button in keyboard_row:
            if keyboard_button.callback_data == f"deployer:chain":
                if "✅" not in keyboard_button.text:
                    keyboard_button.text += " ✅"
    set_keyboard_state(user_id, keyboard)
    set_contract_detail(user_id, "chain", chain)
    contract_message = update_contract_message(user_id)
    await state.clear()
    await callback.message.answer(
        contract_message,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def deploy_callback(callback: CallbackQuery, state: FSMContext):
    print("Deploying Contract...")
    preload_message = await callback.message.answer("Please wait...")
    user_id = callback.from_user.id
    action = callback.data.split(':')[1]
    if action == "cancel":
        delete_contract_details(user_id)
        delete_keyboard_state(user_id)
        await callback.message.answer(
            "Cancelling Contract Deployment...",
            reply_markup=main_menu()
        )
        await state.clear()
        return
    
    contract_details = get_contract_details(user_id)
    private_key = get_private_key(user_id)
    valid = validate_contract_details(contract_details)
    if not valid:
        await callback.message.answer(
            "Incomplete Contract Specs. Please review and try again!",
            reply_markup=deployer_menu(user_id)
        )
        return
    # Pass contract details to contract deployer via API
    data = {'deployer_key': f"0x{private_key}", 'config': contract_details}
    await preload_message.edit_text("Compiling Smart Contract...")
    response = post(deploy_endpoint, json=data)
    if response.ok == False:
        await preload_message.edit_text("An error occured while deploying your contract. Please try again later.")
        keyboard = deployer_menu(user_id)
        contract_message = update_contract_message(user_id)
        await callback.message.answer(
            f"Please reconfirm your contract details\n{contract_message}",
            reply_markup=keyboard)
        return
    
    # Get contract address from API
    res = response.json()
    await preload_message.edit_text(f"Deploying {contract_details['token_name']} at {res['data']}", parse_mode='Markdown')
    # Add contract to database
    add_contract(user_id, res['data'])
    add_contract_details(res['data'], contract_details, private_key)
    delete_contract_details(user_id)
    delete_keyboard_state(user_id)
    await callback.message.answer(
        f"Deployed {contract_details['token_name']} at `{res['data']}`",
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )
    await state.clear()






