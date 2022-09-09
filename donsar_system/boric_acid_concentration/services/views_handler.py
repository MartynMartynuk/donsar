import datetime


def get_epoch_time(date_time: datetime) -> float:
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (date_time - epoch).total_seconds() * 1000.0


def get_datetime_axis(lst, start_time):
    datetime_axis = []
    for minute in lst:
        datetime_axis.append(start_time + datetime.timedelta(minutes=minute))
    return datetime_axis


def get_int_lst(lst):
    int_lst = []
    for i in lst:
        int_lst.append(int(i))
    return int_lst
