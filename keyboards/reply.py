from utils.naming import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.database import db
from config.config_reader import config

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_list

def get_main_keyboard(user_id: int):
    builder = ReplyKeyboardBuilder()
    builder.button(text=MENU_BTN)
    builder.button(text=WHICH_WEEK_BTN)
    builder.button(text=APPEAL_BTN)
    builder.button(text=SCHEDULE_RINGS_BTN)

    if is_admin(user_id):
        builder.button(text=LOAD_MENU_BTN)
    builder.adjust(2) 
    return builder.as_markup(resize_keyboard=True)