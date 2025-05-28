import logging
from utils.naming import *
from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from utils.database import db
from config.config_reader import config
from keyboards.reply import get_main_keyboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_list

class MenuStates(StatesGroup):
    waiting_for_menu = State()
    waiting_for_description = State()

class AnswerStates(StatesGroup):
    waiting_answer = State()

@router.message(F.text == LOAD_MENU_BTN)
async def request_menu_upload(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещён")
        return
    
    await message.answer(
        "Отправьте фото меню (одно или несколько). Затем можно отправить описание.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(MenuStates.waiting_for_menu)
    await state.update_data(menu_photos=[])

@router.message(MenuStates.waiting_for_menu, F.photo)
async def handle_menu_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu_photos = data.get("menu_photos", [])
    menu_photos.append(message.photo[-1].file_id)
    await state.update_data(menu_photos=menu_photos)
    
    await message.answer(
        "Фото принято. Можете отправить еще фото или текст описания.\n"
        "Для завершения нажмите /done",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@router.message(MenuStates.waiting_for_menu, F.text)
async def handle_menu_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu_photos = data.get("menu_photos", [])
    
    if not menu_photos:
        await message.answer("Сначала отправьте хотя бы одно фото меню")
        return
    if message.text == '/done':
        description = ''
    else:
        description = message.text
    db.save_menu(menu_photos, description)
    await message.answer(
        MENU_REFRESH_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    await state.clear()
    

@router.message(MenuStates.waiting_for_menu, Command("done"))
async def finish_menu_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu_photos = data.get("menu_photos", [])
    
    if not menu_photos:
        await message.answer("Не было получено фото меню")
        await state.clear()
        return
    
    db.save_menu(menu_photos, "")
    await message.answer(
        MENU_REFRESH_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    await state.clear()

@router.callback_query(F.data == 'ansver_anon')
async def answer_user_start(callback: CallbackQuery, state: FSMContext, bot):
    message_id = callback.message.message_id
    original_text = callback.message.text
    await state.set_state(AnswerStates.waiting_answer)
    await state.update_data(message_id=message_id, original_text=original_text)
    await callback.message.answer("Введите ответ на обращение:")
    await callback.answer()
    
@router.message(AnswerStates.waiting_answer, F.text)
async def answer_user(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    message_id = data.get('message_id')
    original_text = data.get('original_text')
    if not message_id:
        await message.reply("Ошибка: не удалось определить обращение.")
        await state.finish()
        return
    user_id = db.get_user_for_answer(message_id=message_id)[0][0]
    await bot.edit_message_text(
            chat_id=config.GROUP_ID,
            message_id=message_id,
            text=f'{original_text}\n\n Ответ на обращение был дан админом: {message.from_user.full_name}')
    await message.answer(
        "Сообщение было доставлено пользователю!",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    await bot.send_message(
                chat_id=user_id,
                text=f"📨 Поступил ответ на ваше обращение:\n{message.text}"
            )