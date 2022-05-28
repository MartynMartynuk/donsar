import datetime


def get_start_time(start_time, stop_time):
    minutes_in_hour = 1440
    return int((start_time - stop_time).days * minutes_in_hour +
               (start_time - stop_time).seconds / 60)


def get_maximum_time(start_time):
    return start_time + start_time // 2 + 1


def get_datetime_axis(lst, stop_time):
    datetime_axis = []
    for minute in lst:
        datetime_axis.append(stop_time + datetime.timedelta(minutes=minute))
    return datetime_axis


def get_int_lst(lst):
    int_lst = []
    for i in lst:
        int_lst.append(int(i))
    return int_lst
