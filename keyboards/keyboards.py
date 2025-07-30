from aiogram.types import (CallbackQuery, Message,
                           InlineKeyboardButton, InlineKeyboardMarkup)
def week_btns():
    mon_btn = InlineKeyboardButton(
                text='ПН',
                callback_data='mon'
            )
    tue_btn = InlineKeyboardButton(
                text='ВТ',
                callback_data='tue'
            )
    wed_btn = InlineKeyboardButton(
                text='СР',
                callback_data='wed'
            )
    thu_btn = InlineKeyboardButton(
                text='ЧТ',
                callback_data='thu'
            )
    fri_btn = InlineKeyboardButton(
                text='ПТ',
                callback_data='fri'
            )
    sat_btn = InlineKeyboardButton(
                text='СБ',
                callback_data='sat'
            )
    sun_btn = InlineKeyboardButton(
                text='ВС',
                callback_data='sun'
            )
    return [[mon_btn, tue_btn, wed_btn],[thu_btn, fri_btn],[sat_btn, sun_btn]]

def three_btns():
    day_btn = InlineKeyboardButton(
        text='Ежедневно',
        callback_data='day'
    )
    week_btn = InlineKeyboardButton(
        text='Еженедельно',
        callback_data='week'
    )
    month_btn = InlineKeyboardButton(
        text='Ежемесячно',
        callback_data='month'
    )
    return [[day_btn, week_btn, month_btn]]

def cnts_btns():
    yes_btn = InlineKeyboardButton(
        text='Нужно',
        callback_data='need'
    )
    no_btn = InlineKeyboardButton(
        text='Не нужно',
        callback_data='not_need'
    )
    return [[yes_btn, no_btn]]
