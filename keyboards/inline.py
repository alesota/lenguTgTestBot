from utils.naming import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import db
from config.config_reader import config

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_list

def get_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=ANSWER_ANON, callback_data='ansver_anon')
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_inline_sub():
    builder = InlineKeyboardBuilder()
    builder.button(text=SUB_BTN, url=f'https://t.me/{config.CHANNEL}')
    builder.adjust(1)
    print(f'https://t.me/{config.CHANNEL}')
    return builder.as_markup(resize_keyboard=True)