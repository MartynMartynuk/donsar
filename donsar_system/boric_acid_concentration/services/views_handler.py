import datetime


def get_epoch_time(date_time: datetime) -> float:
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (date_time - epoch).total_seconds() * 1000.0


def get_datetime_time(epoch_time: float) -> datetime:
    return datetime.datetime.utcfromtimestamp(int(epoch_time/1000)) \
           + datetime.timedelta(hours=4)   # для очевидного подгона времени
