from tkinter import ttk
from .constants import *


class Settings:
    def __init__(self):
        self._running = True
        self._root = None
        self._tree_head_stl = None
        self._tree_body_stl = None
        self._table_adder = 0

        self._text_size = None
        self._ping_sleep_timer = None
        self._ping_timeout = None
        self._ping_buffer_size = None
        self._ping_ttl = None
        self._statistics_capacity = None
        self._num_of_tables = None
        self._min_threshold = None
        self._max_threshold = None
        self._log_save = None
        self._log_ignore_dock = None
        self.config_params = self._read_settings_file()

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, running):
        self._running = running

    @property
    def tree_head_stl(self):
        return self._tree_head_stl

    @property
    def tree_body_stl(self):
        return self._tree_body_stl

    @property
    def table_adder(self):
        last = self._table_adder
        self._table_adder = (self._table_adder + 1) % self._num_of_tables
        return last

    def reset_adder(self):
        self._table_adder = 0

    @staticmethod
    def _read_settings_file():
        items = {}
        try:
            with open(SETTINGS_FILE, 'r') as my_file:
                for line in my_file:
                    key, value = line.strip('\n').split('=')
                    items[key] = int(value)
        except (OSError, ValueError):
            items = DEFAULT_SETTINGS
        return items

    def set_text_size(self, new_text_size):
        self._text_size = new_text_size
        self._set_config()

    def set_settings(self, new_settings):
        self.config_params = new_settings
        with open(SETTINGS_FILE, 'w+') as my_file:
            text = '\n'.join([f'{key}={value}' for key, value in self.config_params.items()])
            my_file.write(text)

    def reset_settings(self):
        self.set_settings(DEFAULT_SETTINGS)

    def _set_config(self):
        self._tree_head_stl = ttk.Style()
        self._tree_head_stl.configure('Treeview.Heading',
                                      font=(DEF_TEXT_FONT, self.text_size * TEXT_HEAD_RATIO, 'bold'))
        self._tree_body_stl = ttk.Style()
        self.tree_body_stl.configure('Treeview', font=(DEF_TEXT_FONT, self.text_size, 'bold'),
                                     rowheight=self.text_size * 2)

    @property
    def text_size(self):
        return self._text_size

    @property
    def ping_sleep_timer(self):
        return self._ping_sleep_timer

    @property
    def ping_timeout(self):
        return self._ping_timeout

    @property
    def ping_buffer_size(self):
        return self._ping_buffer_size

    @property
    def ping_ttl(self):
        return self._ping_ttl

    @property
    def statistics_capacity(self):
        return self._statistics_capacity

    @property
    def num_of_tables(self):
        return self._num_of_tables

    @property
    def min_threshold(self):
        return self._min_threshold

    @property
    def max_threshold(self):
        return self._max_threshold

    @property
    def log_save(self):
        return self._log_save

    @property
    def log_ignore_dock(self):
        return self._log_ignore_dock

    @property
    def config_params(self):
        return {Config.TEXT_SIZE: self.text_size,
                Config.SLEEP_TIMER: self.ping_sleep_timer,
                Config.TIMEOUT: self.ping_timeout,
                Config.BUFFER_SIZE: self.ping_buffer_size,
                Config.TTL: self.ping_ttl,
                Config.STATISTICS_CAPACITY: self.statistics_capacity,
                Config.NUM_OF_TABLES: self.num_of_tables,
                Config.MIN_THRESHOLD: self.min_threshold,
                Config.MAX_THRESHOLD: self.max_threshold,
                Config.LOG_SAVE: self._log_save,
                Config.LOG_IGNORE_DOCK: self._log_ignore_dock}

    @config_params.setter
    def config_params(self, config_params):
        self._text_size = config_params[Config.TEXT_SIZE]
        self._ping_sleep_timer = config_params[Config.SLEEP_TIMER]
        self._ping_timeout = config_params[Config.TIMEOUT]
        self._ping_buffer_size = config_params[Config.BUFFER_SIZE]
        self._ping_ttl = config_params[Config.TTL]
        self._statistics_capacity = config_params[Config.STATISTICS_CAPACITY]
        self._num_of_tables = config_params[Config.NUM_OF_TABLES]
        self._min_threshold = config_params[Config.MIN_THRESHOLD]
        self._max_threshold = config_params[Config.MAX_THRESHOLD]
        self._log_save = config_params[Config.LOG_SAVE]
        self._log_ignore_dock = config_params[Config.LOG_IGNORE_DOCK]
        if self._root:
            self._set_config()

    def add_root(self, root):
        self._root = root
        self._set_config()


settings = Settings()
