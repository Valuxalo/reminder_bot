from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Callable, Any, Coroutine
from apscheduler.triggers.cron import CronTrigger
import asyncio
from aiogram import Bot
import pandas as pd
from services.services import cnt_days
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
PATH_TODO_TABLE = "db_data/db_table.csv"

def setup_scheduler() -> AsyncIOScheduler:
    """Инициализация и возврат планировщика"""
    return scheduler

async def send_user_message(bot: Bot, chat_id: int, id: int):
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    row = df.loc[df['id'] == id, 'text'].values[0]
    logger.info("send message")
    if df[df['id'] == id]['cnt_time'].values[0] == 1:
        future_obj = df.loc[df['id'] == id, 'end_time'].values[0]
        print(future_obj)
        ff_row = cnt_days(row, future_obj)
    else:
        ff_row = row
    await bot.send_message(chat_id=chat_id, text=ff_row)

async def add_schedule_for_user(bot: Bot, id: int, chat_id: int, schedule_time: str, next_time: str):
    hour, minute = map(int, next_time.split(':'))
    if schedule_time == '1':
        trigger = CronTrigger(hour=hour, minute=minute, timezone="Europe/Moscow")
        logger.info('time ok')
    elif schedule_time[0] == '7':
        week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        day_of_week = schedule_time[2:5]
        trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
    else:
        day1, day2 = map(int, schedule_time.split())
        trigger = CronTrigger(day=day2, hour=hour, minute=minute)
    scheduler.add_job(
            send_user_message,
            # trigger=CronTrigger(hour=hour, minute=minute, timezone="Europe/Moscow"),
            trigger=trigger,
            args=[bot, chat_id, id],
            id=f"user_{chat_id}_{id}",  # Уникальный ID задачи (чтобы потом удалить)
    )
    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"ID: {job.id}, Next run: {job.next_run_time}, Trigger: {job.trigger}")

async def del_schedule_for_user(id: int, chat_id: int):
    job_id = f"user_{chat_id}_{id}"
    logger.info('del_schedule_for_user: ', chat_id)
    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"ID: {job.id}, Next run: {job.next_run_time}, Trigger: {job.trigger}")
    job = scheduler.get_job(job_id)
    logger.info(f"УДАЛЯЕТСЯ job с ID: {job.id}, Next run: {job.next_run_time}, Trigger: {job.trigger}")
    scheduler.remove_job(job_id)