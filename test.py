from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pandas as pd

PATH_TODO_TABLE = "db_data/db_table.csv"

df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
id = 1
future_obj = df.loc[df['id']== id, 'end_time'].values[0]
print(future_obj)

current_date = datetime.now()
future_date = datetime.strptime(future_obj, "%Y-%m-%d")
time_left = (future_date - current_date).days

print(time_left)