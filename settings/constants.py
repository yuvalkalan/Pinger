from basic import *


class Config(BaseEnum):
    TEXT_SIZE = 'text size'
    SLEEP_TIMER = 'ping sleep timer (ms)'
    TIMEOUT = 'ping timeout (ms)'
    BUFFER_SIZE = 'ping buffer size (bytes)'
    TTL = 'ping ttl'
    STATISTICS_CAPACITY = 'statistics capacity (packets)'
    NUM_OF_TABLES = 'number of tables'
    DOCK_TIME = 'dock time (ms)'
    LOG_SAVE = 'save log (hours)'
    LOG_IGNORE_DOCK = 'ignore dock on log (T/F)'


class Default(BaseEnum):
    STATISTICS_CAPACITY = 100
    TEXT_SIZE = 12
    PING_SLEEP_TIMER = 1000
    PING_TIMEOUT = 4000
    PING_BUFFER_SIZE = 32
    PING_TTL = 128
    NUM_OF_TABLES = 1
    DOCK_TIME = 400
    LOG_SAVE = 72
    LOG_IGNORE_DOCK = 0


class RangeOf(BaseEnum):
    STATISTICS_CAPACITY = (1, 500)
    TEXT_SIZE = (1, 40)
    PING_SLEEP_TIMER = (500, 10000)
    PING_TIMEOUT = (500, 10000)
    PING_BUFFER_SIZE = (32, 65500)
    PING_TTL = (1, 255)
    NUM_OF_TABLES = (1, 5)
    DOCK_TIME = (0, 1000)
    LOG_SAVE = (0, 168)
    LOG_IGNORE_DOCK = (0, 1)


DEFAULT_SETTINGS = {Config.TEXT_SIZE: Default.TEXT_SIZE,
                    Config.SLEEP_TIMER: Default.PING_SLEEP_TIMER,
                    Config.TIMEOUT: Default.PING_TIMEOUT,
                    Config.BUFFER_SIZE: Default.PING_BUFFER_SIZE,
                    Config.TTL: Default.PING_TTL,
                    Config.STATISTICS_CAPACITY: Default.STATISTICS_CAPACITY,
                    Config.NUM_OF_TABLES: Default.NUM_OF_TABLES,
                    Config.DOCK_TIME: Default.DOCK_TIME,
                    Config.LOG_SAVE: Default.LOG_SAVE,
                    Config.LOG_IGNORE_DOCK: Default.LOG_IGNORE_DOCK}

RANGE_OF_SETTINGS = {Config.TEXT_SIZE: RangeOf.TEXT_SIZE,
                     Config.SLEEP_TIMER: RangeOf.PING_SLEEP_TIMER,
                     Config.TIMEOUT: RangeOf.PING_TIMEOUT,
                     Config.BUFFER_SIZE: RangeOf.PING_BUFFER_SIZE,
                     Config.TTL: RangeOf.PING_TTL,
                     Config.STATISTICS_CAPACITY: RangeOf.STATISTICS_CAPACITY,
                     Config.NUM_OF_TABLES: RangeOf.NUM_OF_TABLES,
                     Config.DOCK_TIME: RangeOf.DOCK_TIME,
                     Config.LOG_SAVE: RangeOf.LOG_SAVE,
                     Config.LOG_IGNORE_DOCK: RangeOf.LOG_IGNORE_DOCK}

SETTINGS_FILE = 'settings.txt'
TEXT_HEAD_RATIO = 1
DEF_TEXT_FONT = 'Helvetica'
