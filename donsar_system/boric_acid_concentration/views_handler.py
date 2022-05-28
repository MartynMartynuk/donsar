def get_start_time(start_time, stop_time):
    minutes_in_hour = 1440
    return int((start_time - stop_time).days * minutes_in_hour +
               (start_time - stop_time).seconds / 60)


def get_maximum_time(start_time):
    return start_time + start_time // 2 + 1