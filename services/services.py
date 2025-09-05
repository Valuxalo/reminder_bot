import pandas as pd
from datetime import datetime, timedelta

def delete_data(PATH_TODO_TABLE) -> None:
    df = pd.read_csv(PATH_TODO_TABLE)
    df = df.iloc[0:0]
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')

def cnt_days(row, future_obj):
    current_date = datetime.now()
    future_date = datetime.strptime(future_obj, "%Y-%m-%d")
    time_left = (future_date - current_date).days + 1
    if time_left in [11, 12, 13, 14]:
        ff_row = f"{row}: {time_left} дней"
    elif time_left % 10 == 1:
        ff_row = f"{row}: {time_left} день"
    elif time_left % 10 in [2, 3, 4]:
        ff_row = f"{row}: {time_left} дня"
    else:
        ff_row = f"{row}: {time_left} дней"
    return ff_row