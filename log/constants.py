from basic import Color

LOG_FILE = 'log.txt'

LOG_MODE_R2Y = 'התחבר לתקשורת רציף לאחר נפילה'
LOG_MODE_R2G = 'הרותם עלה'
LOG_MODE_Y2R = 'התנתק מהרציף ונפל'
LOG_MODE_Y2G = 'התנתק מהרציף ועלה'
LOG_MODE_G2R = 'הרותם נפל'
LOG_MODE_G2Y = 'התחבר לתקשורת רציף מרותם'

LOG_MODE_RED = {Color.GRAY: None, Color.RED: None, Color.YELLOW: LOG_MODE_R2Y, Color.GREEN: LOG_MODE_R2G,
                Color.ORANGE: LOG_MODE_R2G}
LOG_MODE_YELLOW = {Color.GRAY: None, Color.RED: LOG_MODE_Y2R, Color.YELLOW: None, Color.GREEN: LOG_MODE_Y2G,
                   Color.ORANGE: LOG_MODE_Y2G}
LOG_MODE_GREEN = {Color.GRAY: None, Color.RED: LOG_MODE_G2R, Color.YELLOW: LOG_MODE_G2Y, Color.GREEN: None,
                  Color.ORANGE: None}
LOG_MODE_ORANGE = {Color.GRAY: None, Color.RED: LOG_MODE_G2R, Color.YELLOW: LOG_MODE_G2Y, Color.GREEN: None,
                   Color.ORANGE: None}
LOG_MODE_GRAY = {Color.GRAY: None, Color.RED: None, Color.YELLOW: None, Color.GREEN: None, Color.ORANGE: None}

LOG_MODES = {
    Color.RED: LOG_MODE_RED,
    Color.YELLOW: LOG_MODE_YELLOW,
    Color.GREEN: LOG_MODE_GREEN,
    Color.ORANGE: LOG_MODE_ORANGE,
    Color.GRAY: LOG_MODE_GRAY
}

MAX_SUBJECT_LENGTH = 27
