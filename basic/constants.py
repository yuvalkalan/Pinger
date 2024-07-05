from typing import *
import enum

COLOR = str
POSITION = Tuple[int, int]


class BaseEnum(enum.Enum):
    def __get__(self, *args, **kwargs):
        return self.value


class Keycodes(BaseEnum):
    A = 65
    SHIFT = 16
    ESCAPE = 27
    LEFT = 37
    UP = 38
    RIGHT = 39
    DOWN = 40
    DELETE = 46


class Modifiers(BaseEnum):
    SHIFT = 'SHIFT'
    CAPS_LOCK = 'CAPS_LOCK'
    CTRL = 'CTRL'
    LEFT_ALT = 'LEFT_ALT'
    NUM_LOCK = 'NUM_LOCK'
    RIGHT_ALT = 'RIGHT_ALT'
    MOUSE_LEFT = 'MOUSE_LEFT'
    MOUSE_MID = 'MOUSE_MID'
    MOUSE_RIGHT = 'MOUSE_RIGHT'
    SCROLL_LOCK = 'SCROLL_LOCK'


class Color(BaseEnum):
    BLACK: COLOR = '#000000'
    RED: COLOR = '#FF0000'
    GREEN: COLOR = '#00FF00'
    BLUE: COLOR = '#0000FF'
    WHITE: COLOR = '#FFFFFF'
    YELLOW: COLOR = '#FFFF00'
    GRAY: COLOR = '#808080'


class Status(BaseEnum):
    CALCULATING = 'Calculating...'
    ONLINE = 'Online'
    OFFLINE = 'Offline'
    PAUSED = 'Paused'


FILE_TYPES = (('Pinger Files (*.pngr)', '*.pngr'), ('All Files (*.*)', '*.*'))

MODIFIER_KEYS = {Modifiers.SHIFT: 1,
                 Modifiers.CAPS_LOCK: 2,
                 Modifiers.CTRL: 4,
                 Modifiers.NUM_LOCK: 8,
                 Modifiers.SCROLL_LOCK: 32,
                 Modifiers.MOUSE_LEFT: 256,
                 Modifiers.MOUSE_MID: 512,
                 Modifiers.MOUSE_RIGHT: 1048,
                 Modifiers.LEFT_ALT: 131072,
                 Modifiers.RIGHT_ALT: 131080}
