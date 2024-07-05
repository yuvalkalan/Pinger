from typing import Tuple
import enum


COLOR = str
POSITION = Tuple[int, int]


class Keycodes(enum.IntEnum):
    A = 65
    SHIFT = 16
    ESCAPE = 27
    LEFT = 37
    UP = 38
    RIGHT = 39
    DOWN = 40
    DELETE = 46


class Modifiers(enum.Enum):
    SHIFT = 'SHIFT'
    CAPS_LOCK = 'CAPS_LOCK'
    CTRL = 'CTRL'
    LEFT_ALT = 'LEFT_ALT'
    MUN_LOCK = 'MUN_LOCK'
    RIGHT_ALT = 'RIGHT_ALT'
    MOUSE_LEFT = 'MOUSE_LEFT'
    MOUSE_MID = 'MOUSE_MID'
    MOUSE_RIGHT = 'MOUSE_RIGHT'
    SCROLL_LOCK = 'SCROLL_LOCK'


class Config(enum.StrEnum):
    TEXT_SIZE = 'text size'
    SLEEP_TIMER = 'ping sleep timer (ms)'
    TIMEOUT = 'ping timeout (ms)'
    BUFFER_SIZE = 'ping buffer size (bytes)'
    DF_FLAG = 'ping df flag (T/F)'
    TTL = 'ping ttl'
    STATISTICS_CAPACITY = 'statistics capacity'
    NUM_OF_TABLES = 'number of tables'
    DOCK_TIME = 'dock time'


class Default(enum.IntEnum):
    STATISTICS_CAPACITY = 100
    TEXT_SIZE = 12
    PING_SLEEP_TIMER = 1000
    PING_TIMEOUT = 4000
    PING_BUFFER_SIZE = 32
    PING_DF_FLAG = 0
    PING_TTL = 128
    NUM_OF_TABLES = 1
    DOCK_TIME = 100


class RangeOf(enum.Enum):
    STATISTICS_CAPACITY = (1, 500)
    TEXT_SIZE = (1, 40)
    PING_SLEEP_TIMER = (500, 10000)
    PING_TIMEOUT = (500, 10000)
    PING_BUFFER_SIZE = (32, 65527)
    PING_DF_FLAG = (0, 1)
    PING_TTL = (1, 255)
    NUM_OF_TABLES = (1, 5)
    DOCK_TIME = (0, 1000)


class Color(enum.StrEnum):
    BLACK: COLOR = '#000000'
    RED: COLOR = '#FF0000'
    GREEN: COLOR = '#00FF00'
    BLUE: COLOR = '#0000FF'
    WHITE: COLOR = '#FFFFFF'
    YELLOW: COLOR = '#FFFF00'
    GRAY: COLOR = '#808080'


class Status(enum.StrEnum):
    CALCULATING = 'Calculating...'
    ONLINE = 'Online'
    OFFLINE = 'Offline'
    PAUSED = 'Paused'


DEF_TEXT_FONT = 'Helvetica'

DEF_TEXT_COLOR = None
DEF_TEXT_BG_COLOR = None
SCREEN_SIZE = '1000x500'
DEF_SCREEN_TITLE = 'Untitled - Pinger++'

ERROR_MSGS = ['destination host unreachable',
              'request timed out',
              'ping request could not find host',
              'ping: transmit failed',
              'general failure',
              'ttl expired in transit',
              'destination net unreachable',
              'destination port unreachable',
              'packet needs to be fragmented but df set']
FILE_TYPES = (('Pinger Files (*.pngr)', '*.pngr'), ('All Files (*.*)', '*.*'))


SETTINGS_FILE = 'settings.txt'
TEXT_HEAD_RATIO = 1

MODIFIER_KEYS = {Modifiers.SHIFT: 1,
                 Modifiers.CAPS_LOCK: 2,
                 Modifiers.CTRL: 4,
                 Modifiers.MUN_LOCK: 8,
                 Modifiers.SCROLL_LOCK: 32,
                 Modifiers.MOUSE_LEFT: 256,
                 Modifiers.MOUSE_MID: 512,
                 Modifiers.MOUSE_RIGHT: 1048,
                 Modifiers.LEFT_ALT: 131072,
                 Modifiers.RIGHT_ALT: 131080}


DEFAULT_SETTINGS = {Config.TEXT_SIZE: Default.TEXT_SIZE,
                    Config.SLEEP_TIMER: Default.PING_SLEEP_TIMER,
                    Config.TIMEOUT: Default.PING_TIMEOUT,
                    Config.BUFFER_SIZE: Default.PING_BUFFER_SIZE,
                    Config.DF_FLAG: Default.PING_DF_FLAG,
                    Config.TTL: Default.PING_TTL,
                    Config.STATISTICS_CAPACITY: Default.STATISTICS_CAPACITY,
                    Config.NUM_OF_TABLES: Default.NUM_OF_TABLES,
                    Config.DOCK_TIME: Default.DOCK_TIME}

RANGE_OF_SETTINGS = {Config.TEXT_SIZE: RangeOf.TEXT_SIZE,
                     Config.SLEEP_TIMER: RangeOf.PING_SLEEP_TIMER,
                     Config.TIMEOUT: RangeOf.PING_TIMEOUT,
                     Config.BUFFER_SIZE: RangeOf.PING_BUFFER_SIZE,
                     Config.DF_FLAG: RangeOf.PING_DF_FLAG,
                     Config.TTL: RangeOf.PING_TTL,
                     Config.STATISTICS_CAPACITY: RangeOf.STATISTICS_CAPACITY,
                     Config.NUM_OF_TABLES: RangeOf.NUM_OF_TABLES,
                     Config.DOCK_TIME: RangeOf.DOCK_TIME}
