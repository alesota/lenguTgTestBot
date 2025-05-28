from utils.naming import *
import datetime
from aiogram import Router, types, F
from keyboards.reply import get_main_keyboard

router = Router()

@router.message(F.text == WHICH_WEEK_BTN)
async def send_week_info(message: types.Message, date=None):
    if date is None:
        date = datetime.date.today()
    week_number = date.isocalendar()[1]
    week_type = "верхняя" if week_number % 2 == 1 else "нижняя"
    await message.answer(
        f"Сегодня: {datetime.date.today()} \nСейчас {week_type} неделя",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
