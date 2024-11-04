from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State

from database.db import add_whitelist
from utils.config import ADMIN_ID

router = Router()
router.message.filter(F.chat.type == "private")

class WhitelistState(StatesGroup):
    setting_whitelist = State() 

from aiogram.types import ForceReply

async def whitelist_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != int(ADMIN_ID):
        return
    await message.answer(
        f"Please enter the user id or username to whitelist",
        reply_markup=ForceReply(selective=True),
    )
    await state.set_state(WhitelistState.setting_whitelist)


async def process_whitelist_callback(message: Message, state: FSMContext):
    text = message.text.strip()
    add_whitelist(text)
    await message.answer(
        f"User {text} has been whitelisted",
        reply_markup=None,
    )
    




