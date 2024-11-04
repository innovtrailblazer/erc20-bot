from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand, BotCommandScopeAllPrivateChats
from utils.config import BOT_NAME

from database.db import init, get_whitelist

# Handlers import
from .wallet import create_wallet_callback, import_wallet_callback, process_import_wallet_callback, WalletStates, main_menu_callback, manage_wallet_callback, process_select_wallet_callback, set_main_wallet_callback
from .contract_deployer import deploy_contract_callback, deployer_contract_handler_callback, process_deployer_contract_handler_callback, chain_select_callback, deploy_callback, DeployerStates
from .contract_editor import manage_contract_callback, select_contract_callback, manage_contracts_callback, call_contract_callback, process_add_excluded_wallet_callback, process_change_tax, process_tax_buy, process_add_liquidity_chain_asset, process_add_liquidity, ContractEditorStates
from .whitelist import whitelist_user, process_whitelist_callback, WhitelistState

router = Router()
router.message.filter(F.chat.type == "private")


async def set_bot_commands(bot: Bot):
    
    # commands = [
    #         BotCommand(command="help", description="All available commands"),
    #         BotCommand(command="wallet", description="Set your wallet"),
    #         BotCommand(command="buy", description="Buy tokens"),
    #         BotCommand(command="sell", description="Sell tokens"),
    #         BotCommand(command="top", description="See trending tokens"),
    # ]
    # await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
    
    return True    

@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    user = get_whitelist(message.from_user.id)
    if user is None:
        print(f"User {message.from_user.id} is not whitelisted")
        return
    # Sends a message to the user, then clears it in line 31
    preload_message = await message.answer("Loading bot...")
    # Clearing state, message already sent by the bot within this context
    init()
    await state.clear()
    await main_menu_callback(message, state)
    
@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer(
        text = f"🚀 *Welcome to {BOT_NAME} on Telegram!* 🚀\n\n",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
   
@router.message(Command(commands=["whitelist"]))
async def cmd_whitelist(message: Message, state: FSMContext):
    await whitelist_user(message, state)
    
@router.message(WhitelistState.setting_whitelist)
async def process_whitelist_wallet(message: Message, state: FSMContext):
    await process_whitelist_callback(message, state)


@router.callback_query(F.data == "main_wallet")
async def manage_wallet(callback: CallbackQuery, state: FSMContext):
    await manage_wallet_callback(callback, state)

@router.callback_query(F.data.startswith("wallet_select:"))
async def wallet_select(callback: CallbackQuery, state: FSMContext):
    await process_select_wallet_callback(callback, state)

@router.callback_query(F.data.startswith("set_main_wallet:"))
async def set_main_wallet(callback: CallbackQuery, state: FSMContext):
    await set_main_wallet_callback(callback, state)

@router.callback_query(F.data == "wallet_create")
async def create_wallet(callback: CallbackQuery, state: FSMContext):
    await create_wallet_callback(callback, state)

@router.callback_query(F.data == "wallet_import")
async def import_wallet(callback: CallbackQuery, state: FSMContext):
    await import_wallet_callback(callback, state)

@router.message(WalletStates.setting_wallet)
async def process_import_wallet(message: Message, state: FSMContext):
    await process_import_wallet_callback(message, state)

@router.callback_query(F.data == "contract_create")
async def create_contract(callback: CallbackQuery, state: FSMContext):
    await deploy_contract_callback(callback, state)

@router.callback_query(F.data.startswith("deployer:"))
async def deployer_contract_handler(callback: CallbackQuery, state: FSMContext):
    await deployer_contract_handler_callback(callback, state)

@router.callback_query(F.data.startswith("chain_select:"))
async def chain_select(callback: CallbackQuery, state: FSMContext):
    await chain_select_callback(callback, state)

@router.callback_query(F.data.startswith("deploy:"))
async def deploy(callback: CallbackQuery, state: FSMContext):
    await deploy_callback(callback, state)

@router.message(DeployerStates.setting_deploy)
async def process_deployer_contract_handler(message: Message, state: FSMContext):
    await process_deployer_contract_handler_callback(message, state)

# Manage Contracts: Select Contract to Manage
@router.callback_query(F.data == "contract_manage")
async def manage_contracts(callback: CallbackQuery, state: FSMContext):
    await manage_contracts_callback(callback, state)

# Selected Contract: Contract_Address
@router.callback_query(F.data.startswith("contract_select:"))
async def select_contract(callback: CallbackQuery, state: FSMContext):
    await select_contract_callback(callback, state)

# Manage Contract: Verify, AddLiquidity, ContractCall
@router.callback_query(F.data.startswith("manage:"))
async def manage_contract(callback: CallbackQuery, state: FSMContext):
    await manage_contract_callback(callback, state)

# Call Contract Function
@router.callback_query(F.data.startswith("contract_call:"))
async def call_contract(callback: CallbackQuery, state: FSMContext):
    await call_contract_callback(callback, state)

# Add Excluded Wallet
@router.message(ContractEditorStates.add_excluded_wallet)
async def add_excluded_wallet(message: Message, state: FSMContext):
    await process_add_excluded_wallet_callback(message, state)

# Change Tax
@router.message(ContractEditorStates.change_tax_buy)
async def change_tax_buy(message: Message, state: FSMContext):
    await process_tax_buy(message, state)

@router.message(ContractEditorStates.change_tax_sell)
async def change_tax_sell(message: Message, state: FSMContext):
    await process_change_tax(message, state)

# Add Liquidity
@router.message(ContractEditorStates.add_liquidity_to_chain_asset)
async def add_liquidity_chain_asset(message: Message, state: FSMContext):
    await process_add_liquidity_chain_asset(message, state)

@router.message(ContractEditorStates.finalize_liquidity_pool)
async def add_liquidity(message: Message, state: FSMContext):
    await process_add_liquidity(message, state)