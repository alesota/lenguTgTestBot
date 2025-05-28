from utils.naming import *
from aiogram import Router, types, F
from aiogram.filters.command import Command
from keyboards.reply import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        START_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )