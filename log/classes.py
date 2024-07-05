from .constants import *
from settings import *
import datetime
import os
import re


class LogFile:
    def __init__(self):
        self._file_name = LOG_FILE
        self._changed = False
        self._times: List[datetime.datetime] = []
        self._lines: List[Tuple[str, str]] = []
        self._read_log()
        self.add('מערכת', 'מתחיל')
        self._start = None
        self._get_start_from_log()

    @property
    def changed(self):
        value = self._changed
        self._changed = False
        return value

    @property
    def hostnames(self):
        content = self.get_string()
        pattern = re.compile(r'(.*) - (.*) - (.*)\n')
        matches = pattern.finditer(content)
        return sorted(list({item.group(2).split(' ')[0] for item in matches}))

    @property
    def start_pos(self):
        return self._start

    def add(self, subject, content):
        self._times.append(datetime.datetime.now())
        self._lines.append((subject.ljust(MAX_SUBJECT_LENGTH), content))
        self._changed = True
        return self

    def update(self):
        # delete log old files
        current_time = datetime.datetime.now()
        while self._times and (current_time - self._times[0]).total_seconds() / 3600 > settings.log_save:
            self._times.pop(0)
            self._lines.pop(0)
            self._changed = True
        # rewrite file if needed
        if self.changed:
            try:
                with open(self._file_name, 'wb+') as log_file:
                    log_file.write(self.get_string().encode())
            finally:
                pass

    def _read_log(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'rb') as log_file:
                content = log_file.read().decode('utf-8')
            pattern = re.compile(r'(.*) - (.*) - (.*)\n')
            matches = pattern.finditer(content)
            for item in matches:
                line_time, line_subject, line_content = item.group(1), item.group(2), item.group(3)
                line_time = datetime.datetime.strptime(line_time, '%d.%m.%Y %H:%M:%S')
                self._times.append(line_time)
                self._lines.append((line_subject, line_content))
        else:
            with open(LOG_FILE, 'w'):
                pass

    def get_string(self):
        log_str = ''
        for i in range(len(self._times)):
            sub, con = self._lines[i]
            log_str += f'{self._times[i].strftime("%d.%m.%Y %H:%M:%S")} - {sub} - {con}\n'
        return log_str

    def get_string_rtl(self):
        log_str = ''
        for i in range(len(self._times)):
            sub, con = self._lines[i]
            new_line = f'זמן: {self._times[i].strftime("%d.%m.%Y %H:%M:%S")} - {sub} - {con}\n'
            log_str += new_line
        return hebrew_reshaper(log_str)

    def _get_start_from_log(self):
        log_content = {}
        with open(LOG_FILE, 'br') as log_file:
            pattern = re.compile(r'(.*) - (.*) - (.*)\n')
            matches = pattern.finditer(log_file.read().decode('utf-8'))
            for item in matches:
                name, time_stamp, value = item.group(2).strip(), item.group(1), item.group(3)
                if value in [LOG_MODE_R2G, LOG_MODE_Y2G, LOG_MODE_G2R, LOG_MODE_G2Y]:
                    log_content[name] = (datetime.datetime.strptime(time_stamp, '%d.%m.%Y %H:%M:%S'), value)
        self._start = log_content


log = LogFile()
