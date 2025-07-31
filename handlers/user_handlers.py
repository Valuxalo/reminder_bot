from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (CallbackQuery, Message,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from lexicon.lexicon import LEXICON
from datetime import datetime, timedelta
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import CommandStart, Command, StateFilter
from services.services import delete_data, cnt_days
from aiogram.enums import ParseMode
from setup_sheduler import add_schedule_for_user, del_schedule_for_user
from keyboards.keyboards import week_btns, three_btns, cnts_btns
# from main import add_schedule_for_user
import pandas as pd
import logging
router = Router()

PATH_TODO_TABLE = "db_data/db_table.csv"

logger = logging.getLogger(__name__)
COUNTER = 1


storage = MemoryStorage()

class FSMFillForm(StatesGroup):
    #перечисляем возможные состояния бота
    fill_task = State()
    fill_time = State() #состояние ожидания ввода имени
    fill_hour = State()
    fill_done = State()
    fill_cnt = State()
    fill_freq = State()

@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON["/start"])
    logger.info('/start')
    
@router.message(Command(commands='add'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    await message.answer(text=LEXICON['add_task'])
    await state.set_state(FSMFillForm.fill_task)
    
@router.message(StateFilter(FSMFillForm.fill_task), F.text)
async def process_add_command(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    text = message.text
    new_data = {'id': [int(COUNTER)], 'user_id': int(message.from_user.id), 'text': [text]}
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    await message.answer(text=LEXICON['add_hour'])
    await state.set_state(FSMFillForm.fill_hour)

@router.message(StateFilter(FSMFillForm.fill_hour), F.text)
async def process_add_command(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    text = message.text
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    df.at[COUNTER - 1, 'next_time'] = text
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    await message.answer(text=LEXICON['add_time'])
    await state.set_state(FSMFillForm.fill_time)

@router.message(StateFilter(FSMFillForm.fill_time), F.text)
async def process_name_sent(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    text = message.text
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y").date()
        print(COUNTER, '___', date_obj)
        df.at[COUNTER - 1, 'end_time'] = date_obj
        df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
        keyboard: list[list[InlineKeyboardButton]] = cnts_btns()
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(text=LEXICON['add_cnt'],
                            reply_markup=markup)
        await state.set_state(FSMFillForm.fill_cnt)
    except ValueError:
        await message.answer(text=LEXICON['not_date'])
    

@router.callback_query(StateFilter(FSMFillForm.fill_cnt), F.data.in_(['need', 'not_need']))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    logger.info(callback.data)
    global COUNTER
    text = 1 if callback.data == 'need' else 0
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    df.at[COUNTER - 1, 'cnt_time'] = text
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    keyboard: list[list[InlineKeyboardButton]] = three_btns()
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer(text=LEXICON['add_freq'],
                                  reply_markup=markup)
    await state.set_state(FSMFillForm.fill_freq)

@router.callback_query(StateFilter(FSMFillForm.fill_freq), F.data.in_(['day', 'week', 'month']))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    logger.info(callback.data)
    global COUNTER
    if callback.data == 'day':
        text = 1
        df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
        freq = str(text)
        df['freq'] = df['freq'].astype(str)
        df.at[COUNTER - 1, 'freq'] =  freq
        end_time = df.at[COUNTER - 1, 'end_time']
        next_time = df.at[COUNTER - 1,  'next_time']
        df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
        await add_schedule_for_user(
            bot = callback.bot,
            id = COUNTER,
            chat_id=callback.from_user.id,
            schedule_time=freq,
            end_date=end_time,
            next_time = next_time
        )
        COUNTER +=1 
        await callback.message.answer(text=LEXICON['reminder_add'])
        await state.clear()
    elif callback.data == 'week':
        keyboard: list[list[InlineKeyboardButton]] = week_btns()
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await callback.message.edit_text(text=LEXICON['add_day_of_week'], reply_markup=markup)
    elif callback.data == 'month':
        await callback.message.answer(text=LEXICON['add_day_of_month'])
    

@router.callback_query(StateFilter(FSMFillForm.fill_freq), F.data.in_(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']))
async def process_name_sent(callback: CallbackQuery, state: FSMContext):
    logger.info(callback.data)
    global COUNTER
    text = '7' + ' ' + str(callback.data)
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    freq = str(text)
    df['freq'] = df['freq'].astype(str)
    df.at[COUNTER - 1, 'freq'] =  freq
    end_time = df.at[COUNTER - 1, 'end_time']
    next_time = df.at[COUNTER - 1,  'next_time']
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    await add_schedule_for_user(
            bot = callback.bot,
            id = COUNTER,
            chat_id=callback.from_user.id,
            schedule_time = freq,
            end_date=end_time,
            next_time = next_time
        )
    COUNTER +=1 
    await callback.message.answer(text=LEXICON['reminder_add'])
    await state.clear()

@router.message(StateFilter(FSMFillForm.fill_freq), F.text.isdigit())
async def process_name_sent(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    text = '9' + ' ' + str(message.text)
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    freq = str(text)
    df['freq'] = df['freq'].astype(str)
    df.at[COUNTER - 1, 'freq'] =  freq
    end_time = df.at[COUNTER - 1, 'end_time']
    next_time = df.at[COUNTER - 1,  'next_time']
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    await add_schedule_for_user(
            bot = message.bot,
            id = COUNTER,
            chat_id=message.chat.id,
            schedule_time = freq,
            end_date=end_time,
            next_time = next_time
        )
    COUNTER +=1 
    await message.answer(text=LEXICON['reminder_add'])
    await state.clear()

@router.message(Command(commands='all'), StateFilter(default_state))
async def process_all_command(message: Message):
    logger.info('/all')
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    filt_df = df[df['user_id'] == int(message.from_user.id)]
    filt_col_df = filt_df[['id', 'text', 'end_time']]
    await message.answer(f"<pre>{filt_col_df.to_markdown(index=False)}</pre>", parse_mode=ParseMode.HTML)

@router.message(Command(commands='done'))
async def process_done_command(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    try:
        num = int(message.text.split(' ', 1)[1])
        if 1 <= num < COUNTER:
            df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
            df = df[df['id'] != num]
            df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
            await del_schedule_for_user(
                id = num,
                chat_id=message.chat.id,
        )
            await message.answer(text=LEXICON['reminder_done'])
            try:
                last_row = df.iloc[-1]
                COUNTER = last_row['id'] + 1
            except:
                COUNTER = 1
        else:
            await message.answer(text=LEXICON['reminder_not_numb'])
        await state.clear()
    except IndexError:
        await message.answer(text=LEXICON['reminder_not_done'])
        await state.set_state(FSMFillForm.fill_done)

@router.message(StateFilter(FSMFillForm.fill_done), F.text.isdigit)
async def process_name_sent(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    num = int(message.text)
    if 1 <= num < COUNTER:
        df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
        df = df[df['id'] != num]
        df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
        await del_schedule_for_user(
                id = num,
                chat_id=message.chat.id,
        )
        await message.answer(text=LEXICON['reminder_done'])
        await state.clear()
        try:
            last_row = df.iloc[-1]
            COUNTER = last_row['id'] + 1
        except:
            COUNTER = 1
    else:
        await message.answer(text=LEXICON['task_not_numb'])

@router.message(Command(commands='clear'))
async def process_cancel_command(message: Message):
    global COUNTER
    logger.info('/clear')
    USER_ID = int(message.from_user.id)
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    ids = df.loc[df['user_id'] == USER_ID, 'id'].tolist()
    for idx in ids:
        await del_schedule_for_user(
                id = idx,
                chat_id=message.chat.id,
        )
    df = df[df['user_id'] != USER_ID]
    try:
        last_row = df.iloc[-1]
        COUNTER = last_row['id'] + 1
    except:
        COUNTER = 1
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    await message.answer(text=LEXICON['clear'])

@router.message()
async def send_echo(message: Message):
    logger.info(F"Uknown text: {message.text}")
    await message.reply(text='Я ничего не понимаю :(')