from collections import namedtuple

ReturnNamedtuple = namedtuple('ReturnNamedtuple', [
    'critical_curve',
    'setting_curve',
    'water_exchange_curve',
    'break_start_time',
    'break_end_time',
    'crit_conc_time',
    'exp_water_exchange',
    'block_'
])

MINUTE_IN_MILLISECONDS = 60000
HOUR_IN_MILLISECONDS = 3600000
