from typing import Callable, Awaitable, Dict, Any
from utils.naming import *
from aiogram import BaseMiddleware
from aiogram.types import Message
from config.config_reader import config
from keyboards.inline import get_inline_sub

class CheckSubscription(BaseMiddleware):
    async def __call__(
            self, 
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], 
            event: Message, 
            data: Dict[str, Any]
    ) -> Any:
        chat_member = await event.bot.get_chat_member(f'@{config.CHANNEL}', event.from_user.id)

        if chat_member.status == 'left':
            await event.answer(f'{SUB_MSG}', reply_markup=get_inline_sub())
        else:
            return await handler(event, data)