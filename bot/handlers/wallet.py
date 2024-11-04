from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State

from utils.blockchain import w3, is_valid_eth_private_key, generate_eth_private_key, get_eth_balances
from utils.config import BOT_NAME
from database.db import add_pKey, get_user, delete_pKey, get_deployer_contracts, set_pKey, get_private_key
from database.keyboard_state import get_pKey_from_uuid
from keyboards.menu import main_menu, generate_menu, deployer_main_menu, select_wallet, set_main_wallet_menu, deployer_wallet_menu
from .utils import format_deployed_tokens_message

router = Router()
router.message.filter(F.chat.type == "private")

class WalletStates(StatesGroup):
    setting_wallet = State() # Will be represented in storage as 'WalletStates:setting_wallet'

class WalletFactory(CallbackData, prefix="wallet"):
    action: str

async def main_menu_callback(message: Message, state: FSMContext):
    username = message.from_user.username
    user_id = message.from_user.id
    user = get_user(user_id)
    if user is None:
        await message.answer(
            f"Hello, {username}! Welcome to {BOT_NAME} 🤖\n\n"
            f"The Ultimate Smart Contract Deployment Bot 🚀\n\n"
            "Please create a wallet to start using this bot.",
            reply_markup=generate_menu(),
            parse_mode='Markdown'
        )
    else:
        private_key = user[1]
        address = w3.eth.account.from_key(private_key).address
        balance = f"Ξ `{w3.from_wei(w3.eth.get_balance(address), 'ether')}`\n\n"
        await message.answer(
        (f"Hello, {username}! Welcome to {BOT_NAME} 🤖\n\n"
        f"The Ultimate Smart Contract Deployment Bot 🚀\n\n"
        "**Your Main Wallet** 👇🏻\n"
        f"✨ `{address}`\nETH Balance\n{balance}"),
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )
    
async def manage_wallet_callback(callback: CallbackQuery, state: FSMContext):
    print("Managing wallet...")
    
    user_id = callback.from_user.id
    user = get_user(user_id)
    if user is None:
        await callback.message.answer(
            "You don't have any wallets to manage. Please create a wallet first.",
            reply_markup=generate_menu(),
            parse_mode='Markdown'
        )
    else:
        private_keys = user[2].split(',')
        wallet_addresses = [w3.eth.account.from_key(pk).address for pk in private_keys]
        balances = get_eth_balances(wallet_addresses)
        address_list = "\n".join(f"{index + 1}. `{address}`\n**Ξ {balances[address]}**" for index, address in enumerate(wallet_addresses))
        view_message = f"**Your Wallets** 👇🏻\n\n{address_list}"
        await callback.message.answer(
            f"Please select the wallet you want to manage.\n\n{view_message}",
            reply_markup=select_wallet(private_keys, 'view'),
            parse_mode='Markdown'
        )

async def create_wallet_callback(callback: CallbackQuery, state: FSMContext):
    print("Creating wallet...")
    
    user_id = callback.from_user.id
    
    preload_message = await callback.message.answer("Generating wallet...")

    private_key = generate_eth_private_key()
    address = w3.eth.account.from_key(private_key).address
    
    await preload_message.edit_text("⏳ Processing...")
    
    # Saving the wallet to the database
    add_pKey(user_id, private_key)
    
    await preload_message.edit_text("⏳ Updating details...")

    await preload_message.edit_text(
        (
            f"✅ Wallet generated successfully!\n\n"
            f"✨ **New Wallet:**\n`{address}`\n\n"
            f"🔒 **Private Key:**\n`0x{private_key}`\n\n"
            "Properly store your private key in a safe place. You will need it to access your wallet."
        ),
        reply_markup=deployer_main_menu(),
        parse_mode='Markdown'
    )


from aiogram.types import ForceReply

async def import_wallet_callback(callback: CallbackQuery, state: FSMContext):
    print("Importing wallet...")
    
    await callback.message.answer(
        "Please enter the private key of the wallet you want to import. Make sure the private key is correct and kept secure.",
        reply_markup=ForceReply(selective=True),
    )
    
    # await WalletStates.setting_wallet.set()
    await state.set_state(WalletStates.setting_wallet)

async def process_import_wallet_callback(message: Message, state: FSMContext):
    
    user_id = message.from_user.id
    private_key = message.text.strip()  # Getting the private key from the user’s message
    
    print(f"User {user_id} is importing wallet {private_key}")
    
    processing_message = await message.answer("⏳ Processing your private key...")
    
    valid_key = is_valid_eth_private_key(private_key)
    
    if valid_key:
        
        await processing_message.edit_text("⏳ Validating and importing wallet...")
        
        # Encrypting and hashing the private key
        wallet_address = w3.eth.account.from_key(private_key).address

        # Saving the wallet to the database
        add_pKey(user_id, valid_key)
        
        await processing_message.edit_text(
            (
                "✅ Wallet generated successfully!\n\n"
                f"✨ **New Wallet:**\n`{wallet_address}`\n\n"
                "You can now deploy a contract or edit an existing contract."
            ),
            parse_mode='Markdown', 
            reply_markup=deployer_main_menu())
        
    else:
        await processing_message.edit_text(
            "❌ Invalid ETH private key. Please ensure the private key is correct and try again.", 
            reply_markup=generate_menu())

async def delete_wallet_callback(callback: CallbackQuery, state: FSMContext):
    print("Deleting wallet...")
    
    user_id = callback.from_user.id
    user = get_user(user_id)
    if user is None:
        await callback.message.edit_text(
            "You don't have any wallets to delete. Please create a wallet first.",
            reply_markup=generate_menu(),
            parse_mode='Markdown'
        )
    else:
        private_keys = user[2].split(',')
        if len(private_keys) == 1:
            await callback.message.edit_text(
                "You only have one wallet. You cannot delete your last wallet.",
                reply_markup=generate_menu()
            )
        else:
            await callback.message.edit_text(
                "Please select the wallet you want to delete.",
                reply_markup=select_wallet(private_keys)
            )

async def process_select_wallet_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    private_key_uuid = callback.data.split(':')[1]
    private_key = get_pKey_from_uuid(private_key_uuid)
    address = w3.eth.account.from_key(private_key).address
    action = callback.data.split(':')[2]
    if action == 'delete':
        delete_pKey(user_id, private_key)
        await callback.message.answer(
            "✅ Wallet deleted successfully!",
            reply_markup=main_menu()
        )
    else:
        main_private_key = get_private_key(user_id)
        is_main = True if main_private_key == private_key else False
        contracts_deployed = get_deployer_contracts(private_key)
        response_message = f"**Your Wallet** 👇🏻\n`{address}`\nPrivate Key: `0x{private_key}`\n\nContracts Deployed\n"
        if contracts_deployed == []:
            keyboard = deployer_main_menu() if is_main else set_main_wallet_menu(private_key)
            await callback.message.answer(f"{response_message}\nThis wallet has no contracts deployed\n\n{'' if is_main else 'Set as Main to deploy contracts'}", reply_markup=keyboard, 
            parse_mode='Markdown')
        else:
            contracts = [{'address': contract[0], 'symbol': contract[3]} for contract in contracts_deployed]
            await callback.message.answer(
            f"{response_message}{format_deployed_tokens_message(contracts_deployed)}\n\n{'' if is_main else 'Set as Main to deploy contracts'}",
            reply_markup=deployer_wallet_menu(contracts, private_key, is_main),
            parse_mode='Markdown'
        )
            
async def set_main_wallet_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    private_key_uuid = callback.data.split(':')[1]
    private_key = get_pKey_from_uuid(private_key_uuid)
    address = w3.eth.account.from_key(private_key).address
    set_pKey(user_id, private_key)
    await callback.message.answer(
        f"✅ Main wallet set to `{address}`",
        reply_markup=deployer_main_menu(),
        parse_mode='Markdown'
    )