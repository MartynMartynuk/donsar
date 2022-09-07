import datetime
from donsar_system.settings import DATE_INPUT_FORMATS


def get_time_in_minutes(start_time, stop_time):
    minutes_in_hour = 1440
    return int((start_time - stop_time).days * minutes_in_hour +
               (start_time - stop_time).seconds / 60)


def get_maximum_time(start_time):
    return start_time + start_time // 2 + 1


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


def datetime_dict_to_lst(dict_):
    datetime_lst = []
    meaning_lst = []
    for i in dict_.keys():
        datetime_lst.append(datetime.datetime.strptime(i, DATE_INPUT_FORMATS[0]))
        meaning_lst.append(dict_[i])
    return datetime_lst, meaning_lst


def get_static_concentration(start_minute: int, end_minute: int, concentration):
    critical_curve = {}
    graph_counter = 0   # счетчик для графика
    for minute in range(start_minute, end_minute+1):
        critical_curve[graph_counter] = {'date': minute, 'value': concentration}
        graph_counter += 1
    return critical_curve

# ToDo Объединить! Dry!
def get_setting_curve(crit_curve: dict, setting_interval):
    setting_curve = {}
    for graph_counter in list(crit_curve.keys()):
        setting_curve[graph_counter] = {'date': crit_curve[graph_counter]['date'],
                                        'value': crit_curve[graph_counter]['value'] + setting_interval}
    return setting_curve
