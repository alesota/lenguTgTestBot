import asyncio
import logging
import datetime
from naming import *
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import ContentType
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from config_reader import config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()

# cостояния для FSM
class AppealStates(StatesGroup):
    waiting_for_appeal = State()

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_list

# основная клавиатура
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


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        START_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )

# обращение для ПрофСовета
@dp.message(F.text == APPEAL_BTN)
async def start_appeal(message: types.Message, state: FSMContext):
    await message.answer(
        "Напишите ваше обращение или отправьте файл/фото/видео. Оно будет отправлено в ПрофСовет анонимно.\n"
        "Для отмены напишите /cancel",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AppealStates.waiting_for_appeal)

# обработчик для всех типов обращений
@dp.message(AppealStates.waiting_for_appeal)
async def handle_appeal(message: types.Message, state: FSMContext):
    try:
        # text
        if message.text and not message.text.startswith('/'):
            await bot.send_message(
                chat_id=config.GROUP_ID,
                message_thread_id=634,
                text=f"{NEW_ANON_MSG}{message.text}"
            )
        
        # photo
        elif message.photo:
            await bot.send_photo(
                chat_id=config.GROUP_ID,
                message_thread_id=634,
                photo=message.photo[-1].file_id,
                caption=f"{NEW_ANON_MSG}{message.caption or 'Без описания'}"
            )
        
        # docs
        elif message.document:
            await bot.send_document(
                chat_id=config.GROUP_ID,
                message_thread_id=634,
                document=message.document.file_id,
                caption=f"{NEW_ANON_MSG}{message.caption or 'Без описания'}"
            )
        
        # video
        elif message.video:
            await bot.send_video(
                chat_id=config.GROUP_ID,
                message_thread_id=634,
                video=message.video.file_id,
                caption=f"{NEW_ANON_MSG}{message.caption or 'Без описания'}"
            )
        
        # voice msg
        elif message.voice:
            await bot.send_voice(
                chat_id=config.GROUP_ID,
                message_thread_id=634,
                voice=message.voice.file_id,
                caption="📨 Новое анонимное голосовое обращение"
            )
        
        else:
            await message.answer("Этот тип сообщения не поддерживается для обращений")
            get_main_keyboard()
            return

        await message.answer(
            APPEAL_SUCCES_MSG,
            reply_markup=get_main_keyboard(message.from_user.id)
        )
    
    except Exception as e:
        logger.error(f"Ошибка при отправке обращения: {e}")
        await message.answer(
            APPEAL_ERROR_MSG,
            reply_markup=get_main_keyboard(message.from_user.id)
        )
    finally:
        await state.clear()


# охрана отмена
@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    get_main_keyboard()
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        CANCEL_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )

#обработка получения и отправки меню
class MenuStates(StatesGroup):
    waiting_for_menu = State()
    waiting_for_description = State()

@dp.message(F.text == LOAD_MENU_BTN)
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

@dp.message(MenuStates.waiting_for_menu, F.photo)
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

@dp.message(MenuStates.waiting_for_menu, F.text)
async def handle_menu_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu_photos = data.get("menu_photos", [])
    
    if not menu_photos:
        await message.answer("Сначала отправьте хотя бы одно фото меню")
        return
    
    description = message.text
    db.save_menu(menu_photos, description)
    await message.answer(
        MENU_REFRESH_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    await state.clear()

@dp.message(MenuStates.waiting_for_menu, Command("done"))
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

@dp.message(F.text == MENU_BTN)
async def send_menu(message: types.Message):
    menu_items = db.get_all_menu_photos()
    if not menu_items:
        await message.answer("Меню пока не загружено")
        return
    
    # Отправляем описание один раз
    description = menu_items[0][1] if menu_items[0][1] else ""
    date_added = menu_items[0][2]
    
    caption = f"🍛 Меню столовой на {date_added[:10]}"
    if description:
        caption += f"\n\n{description}"
    
    # Создаем медиагруппу
    media = []
    for idx, item in enumerate(menu_items):
        if idx == 0:
            media.append(types.InputMediaPhoto(
                media=item[0],
                caption=caption
            ))
        else:
            media.append(types.InputMediaPhoto(
                media=item[0]
            ))
    
    await bot.send_media_group(
        chat_id=message.chat.id,
        media=media
    )


@dp.message(F.text == WHICH_WEEK_BTN)
async def send_week_info(message: types.Message, date=None):
    if date is None:
        date = datetime.date.today()
    week_number = date.isocalendar()[1]
    week_type = "верхняя" if week_number % 2 == 1 else "нижняя"
    await message.answer(
        f"Сегодня: {datetime.date.today()} \nСейчас {week_type} неделя",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message(F.text == SCHEDULE_RINGS_BTN)
async def send_schedule(message: types.Message):
    date_now = datetime.datetime.now()
    await message.answer(
        f"{SCHEDULE_RINGS_MSG}{date_now.strftime('\n\nТекущая дата: %d.%m.%y\nВремя: %H:%M:%S')}",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())