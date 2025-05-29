from utils.naming import *
from aiogram import Router, types, F
from utils.database import db

router = Router()

@router.message(F.text == MENU_BTN)
async def send_menu(message: types.Message, bot):
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