import pandas as pd
import logging
import asyncio
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config.config import Config, load_config
from set_menu import set_main_menu
from lexicon.lexicon import LEXICON
from datetime import datetime, timedelta
from setup_sheduler import setup_scheduler
from services.services import delete_data, cnt_days
from handlers import user_handlers

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token
PATH_TODO_TABLE = "db_data/db_table.csv"
delete_data(PATH_TODO_TABLE)
logger = logging.getLogger(__name__)

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN, 
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def main():

    async def on_startup(dispatcher: Dispatcher, bot: Bot):
        await set_main_menu(bot)
    
        logging.basicConfig(
        handlers=[
            RotatingFileHandler(
                "logs/bot.log",
                maxBytes=5*1024*1024,  # 5 MB
                backupCount=3,
                encoding='utf-8'
            )
        ],
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
    '[%(asctime)s] - %(name)s -%(message)s')

    scheduler = setup_scheduler()

    dp.include_router(user_handlers.router)
    global logger
    logger = logging.getLogger(__name__)
    logger.info('Starting bot') #начало работы бота
    scheduler.start()
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())