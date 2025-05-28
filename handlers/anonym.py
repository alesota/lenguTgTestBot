import logging
from utils.naming import *
from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.database import db
from config.config_reader import config
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_inline_keyboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = Router()

class AppealStates(StatesGroup):
    waiting_for_appeal = State()

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_list

@router.message(Command("cancel") or F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    get_main_keyboard(message.from_user.id)
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        CANCEL_MSG,
        reply_markup=get_main_keyboard(message.from_user.id)
    )

# обращение для ПрофСовета
@router.message(F.text == APPEAL_BTN)
async def start_appeal(message: types.Message, state: FSMContext):
    chat = message.chat
    if chat.type != 'private':
        await message.answer("Обращение можно вызвать только в личных сообщениях!")
        return
    await message.answer(
        "Напишите ваше обращение или отправьте файл/фото/видео. Оно будет отправлено в ПрофСовет анонимно.\n"
        "Для отмены напишите /cancel",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AppealStates.waiting_for_appeal)

# обработчик для всех типов обращений
@router.message(AppealStates.waiting_for_appeal)
async def handle_appeal(message: types.Message, state: FSMContext, bot):
    try:
        # text
        if message.text and not message.text.startswith('/'):
            appeal = await bot.send_message(
                chat_id=config.GROUP_ID,
                #message_thread_id=634,
                text=f"{NEW_ANON_MSG}{message.text}",
                reply_markup=get_inline_keyboard()
            )
            db.save_anonym_message(message.from_user.id, message_id=appeal.message_id, message=message.text)
        
        # photo
        elif message.photo:
            await bot.send_photo(
                chat_id=config.GROUP_ID,
                #message_thread_id=634,
                photo=message.photo[-1].file_id,
                caption=f"{NEW_ANON_MSG}{message.caption or 'Без описания'}"
            )
        
        # docs
        elif message.document:
            await bot.send_document(
                chat_id=config.GROUP_ID,
                #message_thread_id=634,
                document=message.document.file_id,
                caption=f"{NEW_ANON_MSG}{message.caption or 'Без описания'}"
            )
        
        # video
        elif message.video:
            await bot.send_video(
                chat_id=config.GROUP_ID,
                #message_thread_id=634,
                video=message.video.file_id,
                caption=f"{NEW_ANON_MSG}{message.caption or 'Без описания'}"
            )
        
        # voice msg
        elif message.voice:
            await bot.send_voice(
                chat_id=config.GROUP_ID,
                #message_thread_id=634,
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