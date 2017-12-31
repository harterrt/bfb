import os
import pandas as pd
import calendar
from functional import seq

def summarize_month(date, data_path):
    dates = filter(
        lambda x: x.month == date.month,
        calendar.Calendar().itermonthdates(date.year, date.month)
    )

    month_data = pd.concat(
        seq(dates)
        .map(lambda x: os.path.join(data_path, x.strftime('%Y-%m-%d.csv')))
        .map(safe_read)
        .filter(lambda x: x is not None)
    )

    report = (
        month_data
        .groupby(['name', 'volume'])['price']
        .agg('count')
    )

    return report

def safe_read(path):
    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, IOError):
        return None

