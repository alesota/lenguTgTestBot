from utils.naming import *
import datetime
from aiogram import Router, types, F
from keyboards.reply import get_main_keyboard

router = Router()

@router.message(F.text == SCHEDULE_RINGS_BTN)
async def send_schedule(message: types.Message):
    date_now = datetime.datetime.now()
    formated_date = date_now.strftime('\n\nТекущая дата: %d.%m.%y\nВремя: %H:%M:%S')
    await message.answer(
        text=f"{SCHEDULE_RINGS_MSG}{formated_date}",
        reply_markup=get_main_keyboard(message.from_user.id)
    )