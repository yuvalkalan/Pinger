from basic import Color


LOG_FILE = 'log.txt'


LOG_MODE_R2Y = 'התחבר לתקשורת רציף לאחר נפילה'
LOG_MODE_R2G = 'הרותם עלה'
LOG_MODE_Y2R = 'התנתק מהרציף ונפל'
LOG_MODE_Y2G = 'התנתק מהרציף ועלה'
LOG_MODE_G2R = 'הרותם נפל'
LOG_MODE_G2Y = 'התחבר לתקשורת רציף מרותם'

LOG_MODES = {Color.RED: {Color.GRAY: None, Color.RED: None, Color.YELLOW: LOG_MODE_R2Y, Color.GREEN: LOG_MODE_R2G},
             Color.YELLOW: {Color.GRAY: None, Color.RED: LOG_MODE_Y2R, Color.YELLOW: None, Color.GREEN: LOG_MODE_Y2G},
             Color.GREEN: {Color.GRAY: None, Color.RED: LOG_MODE_G2R, Color.YELLOW: LOG_MODE_G2Y, Color.GREEN: None},
             Color.GRAY: {Color.GRAY: None, Color.RED: None, Color.YELLOW: None, Color.GREEN: None}}

MAX_SUBJECT_LENGTH = 27
