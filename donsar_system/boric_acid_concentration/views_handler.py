import datetime
from donsar_system.settings import DATE_INPUT_FORMATS


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


def datetime_dict_to_lst(dict_):
    datetime_lst = []
    meaning_lst = []
    for i in dict_.keys():
        datetime_lst.append(datetime.datetime.strptime(i, DATE_INPUT_FORMATS[0]))
        meaning_lst.append(dict_[i])
    return datetime_lst, meaning_lst
