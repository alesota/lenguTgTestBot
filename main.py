import asyncio
import logging
from utils.naming import *
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.config_reader import config
from handlers import admin, anonym, schedule, start, week, canteen, hideKeyboard


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()
dp.include_routers(
        anonym.router,
        start.router,
        week.router,
        canteen.router,
        admin.router,
        schedule.router,
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())