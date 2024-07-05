import datetime
import os
import subprocess
import threading
import time
from typing import List, Optional, Tuple, Dict
import tkinter as tk
from tkinter import filedialog as fd, messagebox as msgbox, ttk

COLOR = str
POSITION = Tuple[int, int]

BLACK: COLOR = '#000000'
RED: COLOR = '#FF0000'
GREEN: COLOR = '#00FF00'
BLUE: COLOR = '#0000FF'
WHITE: COLOR = '#FFFFFF'
YELLOW: COLOR = '#FFFF00'
GRAY: COLOR = '#808080'

DEF_TEXT_FONT = 'Helvetica'

DEF_TEXT_COLOR = None
DEF_TEXT_BG_COLOR = None
SCREEN_SIZE = '1000x500'
SCREEN_TITLE = 'BetterPinger'

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
MODIFIER_KEYS = {SHIFT: 1, CAPS_LOCK: 2, CTRL: 4, MUN_LOCK: 8, SCROLL_LOCK: 32, MOUSE_LEFT: 256, MOUSE_MID: 512,
                 MOUSE_RIGHT: 1048, LEFT_ALT: 131072, RIGHT_ALT: 131080}

KEYCODE_ESCAPE = 27
KEYCODE_DELETE = 46

DOCK_PARAM = 100

CALCULATING = 'Calculating...'
ONLINE = 'Online'
OFFLINE = 'Offline'
PAUSED = 'Paused'

DEF_SCROLL_SENSITIVITY = 120
DEF_STATISTICS_CAPACITY = 100

DEF_TEXT_SIZE = 12

DEF_PING_SLEEP_TIMER = 1
DEF_PING_TIMEOUT = 2
DEF_PING_BUFFER_SIZE = 32
DEF_PING_DF_FLAG = 0
DEF_PING_TTL = 128

SETTINGS_FILE = 'settings.txt'

CONFIG_TEXT_SIZE = 'text size'
CONFIG_SLEEP_TIMER = 'ping sleep timer (sec)'
CONFIG_TIMEOUT = 'ping timeout (sec)'
CONFIG_BUFFER_SIZE = 'ping buffer size (bytes)'
CONFIG_DF_FLAG = 'ping df flag (0/1)'
CONFIG_TTL = 'ping ttl'
CONFIG_SCROLL_SENSITIVITY = 'scroll sensetivity'
CONFIG_STATISTICS_CAPACITY = 'statistics capacity'


class Settings:
    def __init__(self):
        self._running = True
        self._root = None
        self._tree_head_stl = None
        self._tree_body_stl = None
        self._normal_text_stl = None

        self._text_size = None
        self._ping_sleep_timer = None
        self._ping_timeout = None
        self._ping_buffer_size = None
        self._ping_df_flag = None
        self._ping_ttl = None
        self._scroll_sensetivity = None
        self._statistics_capacity = None
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
    def normal_text_stl(self):
        return self._normal_text_stl

    @staticmethod
    def _read_settings_file():
        items = {}
        try:
            with open(SETTINGS_FILE, 'r') as my_file:
                for line in my_file:
                    key, value = line.split('=')
                    items[key] = int(value)
        except (OSError, ValueError):
            items = {CONFIG_TEXT_SIZE: DEF_TEXT_SIZE,
                     CONFIG_SLEEP_TIMER: DEF_PING_SLEEP_TIMER,
                     CONFIG_TIMEOUT: DEF_PING_TIMEOUT,
                     CONFIG_BUFFER_SIZE: DEF_PING_BUFFER_SIZE,
                     CONFIG_DF_FLAG: DEF_PING_DF_FLAG,
                     CONFIG_TTL: DEF_PING_TTL,
                     CONFIG_SCROLL_SENSITIVITY: DEF_SCROLL_SENSITIVITY,
                     CONFIG_STATISTICS_CAPACITY: DEF_STATISTICS_CAPACITY}
        return items

    def set_settings(self, new_settings):
        self.config_params = new_settings
        with open(SETTINGS_FILE, 'w+') as my_file:
            text = '\n'.join([f'{key}={value}' for key, value in self.config_params.items()])
            my_file.write(text)

    def reset_settings(self):
        try:
            os.remove(SETTINGS_FILE)
        except FileNotFoundError:
            pass
        self.config_params = self._read_settings_file()

    def _set_config(self):
        self._tree_head_stl = ttk.Style()
        self._tree_head_stl.configure("Treeview.Heading", font=(DEF_TEXT_FONT, self.text_size * 2, 'bold'))

        self._tree_body_stl = ttk.Style()
        self._tree_body_stl.configure("Treeview", font=(DEF_TEXT_FONT, self.text_size, 'bold'),
                                      rowheight=self.text_size * 2)

        self._normal_text_stl = ttk.Style()
        self._normal_text_stl.configure("TEntry", font=(DEF_TEXT_FONT, self.text_size, 'bold'))

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
    def ping_df_flag(self):
        return self._ping_df_flag

    @property
    def ping_ttl(self):
        return self._ping_ttl

    @property
    def scroll_sensetivity(self):
        return self._scroll_sensetivity

    @property
    def statistics_capacity(self):
        return self._statistics_capacity

    @property
    def ping_command(self):
        return 'ping -n 1 -l {} {} -i {} -w {}'.format(self.ping_buffer_size,
                                                       "-f" if self.ping_df_flag else "",
                                                       self.ping_ttl,
                                                       self.ping_timeout * 1000)

    @property
    def config_params(self):
        return {CONFIG_TEXT_SIZE: self.text_size,
                CONFIG_SLEEP_TIMER: self.ping_sleep_timer,
                CONFIG_TIMEOUT: self.ping_timeout,
                CONFIG_BUFFER_SIZE: self.ping_buffer_size,
                CONFIG_DF_FLAG: self.ping_df_flag,
                CONFIG_TTL: self.ping_ttl,
                CONFIG_SCROLL_SENSITIVITY: self.scroll_sensetivity,
                CONFIG_STATISTICS_CAPACITY: self.statistics_capacity}

    @config_params.setter
    def config_params(self, config_params):
        self._text_size = config_params[CONFIG_TEXT_SIZE]
        self._ping_sleep_timer = config_params[CONFIG_SLEEP_TIMER]
        self._ping_timeout = config_params[CONFIG_TIMEOUT]
        self._ping_buffer_size = config_params[CONFIG_BUFFER_SIZE]
        self._ping_df_flag = config_params[CONFIG_DF_FLAG]
        self._ping_ttl = config_params[CONFIG_TTL]
        self._scroll_sensetivity = config_params[CONFIG_SCROLL_SENSITIVITY]
        self._statistics_capacity = config_params[CONFIG_STATISTICS_CAPACITY]
        if self._root:
            self._set_config()

    def add_root(self, root):
        self._root = root
        self._set_config()


settings = Settings()


class Text:
    def __init__(self, master, text, pos, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR, size=settings.text_size):
        self._text = text
        self._color = color
        self._pos = pos
        self._bg_color = bg_color
        self._bg_color_changed = False
        self._font = (DEF_TEXT_FONT, size)
        self._widget = tk.Entry(master, fg=color, readonlybackground=bg_color, font=self._font, bd=0)
        self._widget.insert(0, text)
        self._widget.config(state='readonly')
        self._is_dead = False

    def draw(self, **kwargs):
        row, column = self._pos
        self._widget.grid(row=row, column=column, **kwargs)

    def pack(self, *args, **kwargs):
        self._widget.pack(*args, **kwargs)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._widget.config(state='normal')
        self._widget.delete(0, tk.END)
        self._widget.insert(0, text)
        self._widget.config(state='readonly')

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, bg_color):
        self._bg_color_changed = self._bg_color != bg_color or self._bg_color_changed
        self._bg_color = bg_color

    @property
    def bg_color_changed(self):
        res = self._bg_color_changed
        self._bg_color_changed = False
        return res

    @property
    def widget(self):
        return self._widget

    def change_background(self):
        self._widget.config(readonlybackground=self._bg_color)

    def destroy(self):
        self._widget.destroy()

    def bind(self, event, handler):
        self._widget.bind(event, handler)


class Button(Text):
    def __init__(self, master, text, pos, func, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR,
                 size=settings.text_size):
        super(Button, self).__init__(master, text, pos, color, bg_color, size)
        self._func = func
        self._widget = tk.Button(master, text=text, fg=color, bg=bg_color, command=func, font=self._font)


class InputBox(Text):
    def __init__(self, master, text, pos, color=BLACK, bg_color=DEF_TEXT_BG_COLOR, size=settings.text_size):
        super(InputBox, self).__init__(master, text, pos, color, bg_color, size)
        self._widget = tk.Entry(master, fg=GRAY, bg=bg_color, font=self._font)
        self._widget.insert(0, text)
        self._changed = False
        self._widget.bind('<FocusIn>', self._got_focus)

    def _got_focus(self, _):
        if not self._changed:
            self._changed = True
            self._widget.delete(0, tk.END)
            self._widget.config(foreground=self._color)

    def reset_text(self):
        self._widget.delete(0, tk.END)
        self._widget.insert(0, self._text)
        self._widget.config(foreground=GRAY)
        self._changed = False

    @property
    def value(self):
        return self._widget.get()

    @property
    def changed(self):
        return self._changed


class Table:
    def __init__(self, master: tk.Misc, titles, pos):
        row, column = pos
        # make table resizable
        master.grid_rowconfigure(row, weight=1)
        self._master = master
        self._frame = tk.Frame(master)
        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid(row=row, column=column, sticky=tk.NSEW)
        # create tree
        self._tree = ttk.Treeview(self._frame, columns=titles, show='headings')
        for column in titles:
            self._tree.heading(column, text=column)
        self._tree.grid(row=0, column=0, sticky=tk.NSEW)
        # add a scrollbar
        self._scrollbar = ttk.Scrollbar(self._frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.grid(row=0, column=1, sticky='ns')
        self._menu = tk.Menu(self._frame, tearoff=False)
        self._menu.add_command(label='remove', command=self._remove_cmd)
        self._menu.add_command(label='edit name', command=self._edit_name_cmd)
        self._menu.add_command(label='forward', command=self._forward_cmd)
        self._menu.add_command(label='backward', command=self._backward_cmd)
        self._tree.bind('<Button-3>', lambda e: self._menu.tk_popup(e.x_root, e.y_root))

    def _popup_menu(self, event):
        iid = self._tree.identify_row(event.y)
        if iid:
            self._tree.selection_set(iid)

    def _remove_cmd(self):
        for iid in self._tree.selection():
            self._tree.delete(iid)

    def _edit_name_cmd(self):
        pass

    def _forward_cmd(self):
        pass

    def _backward_cmd(self):
        pass

    def add(self, line):
        return self._tree.insert('', tk.END, values=line)


class PingTable(Table):
    def __init__(self, master: tk.Misc, pos):
        super(PingTable, self).__init__(master, ('Host Name', 'Ip Address', 'Status', 'Statistics (%)'), pos)
        self._master.after(100, self._check_pingers)
        self._ping_threads: List[threading.Thread] = []
        self._item_indexes: Dict[str, PingTableLine] = {}

        self._tree.tag_configure(GREEN, background=GREEN)
        self._tree.tag_configure(YELLOW, background=YELLOW)
        self._tree.tag_configure(RED, background=RED)
        self._tree.bind('<Double-Button-1>', self._open_sub_window)
        self._tree.bind('<KeyPress>', self._check_keypress)

        self._menu.add_command(label='pause/resume', command=self._pause_cmd)

        self._have_changed = False

    @property
    def have_changed(self):
        return self._have_changed

    @have_changed.setter
    def have_changed(self, value):
        self._have_changed = value

    def _pause_cmd(self):
        for iid in self._tree.selection():
            self._item_indexes[iid].pause = not self._item_indexes[iid].pause

    def _remove_cmd(self):
        for iid in self._tree.selection():
            self._tree.delete(iid)
            self._item_indexes.pop(iid).kill()
        self._have_changed = True

    def _open_sub_window(self, event: tk.Event):
        pressed_keys = check_keyboard(event)
        if not pressed_keys[CTRL]:
            iids = self._tree.selection()
            if len(iids) == 1:
                line = self._item_indexes[iids[0]]
                line.create_window()

    def _check_keypress(self, event: tk.Event):
        pressed_keys = check_keyboard(event)
        if event.keycode == ord('A') and pressed_keys[CTRL]:
            self._tree.selection_set(self._tree.get_children())
        elif event.keycode == KEYCODE_ESCAPE:
            self._tree.selection_set([])
        elif event.keycode == KEYCODE_DELETE:
            self._remove_cmd()
        # else:
        #     print(event)

    def add(self, host_name_and_ip_address):
        name, ip = host_name_and_ip_address

        index = super(PingTable, self).add([name, ip, CALCULATING, '?%'])
        new_line = PingTableLine(self._master, self, name, ip, index)
        self._item_indexes[index] = new_line

        self._have_changed = True

        thread = threading.Thread(target=pinger_thread, args=[new_line])
        self._ping_threads.append(thread)
        thread.start()

    def join(self):
        for thread in self._ping_threads:
            thread.join()

    def reset(self):
        for line in self._item_indexes.values():
            line.kill()
        for i in self._tree.get_children():
            self._tree.delete(i)
        self._item_indexes = {}

    def _submit_updates(self, index, color, name, ip, status, statistics):
        self._tree.delete(index)
        self._tree.insert('', tk.END, iid=index, values=[name, ip, status, statistics], tags=[color])

    def _check_pingers(self):
        selections = self._tree.selection()
        for iid in self._item_indexes:
            line = self._item_indexes[iid]
            self._submit_updates(*line.values)
            line.add_data_to_window()
        self._tree.selection_set(selections)
        self._master.after(500 * settings.ping_sleep_timer, self._check_pingers)

    @property
    def items(self):
        return [(line.host_name, line.ip_address) for line in self._item_indexes.values()]


class Statistics:
    def __init__(self):
        self._values = []
        self._index = 0

    def __iadd__(self, other):
        value = 1 if other else 0
        if len(self._values) < settings.statistics_capacity:
            self._values.append(value)
        else:
            self._values[self._index] = value
            self._index = (self._index + 1) % len(self._values)
        return self

    @property
    def value(self):
        if self._values:
            return str(round((sum(self._values) / len(self._values)) * 100)).zfill(3) + '%'
        return '???%'


class PingTableLine:
    def __init__(self, root, table, host_name, ip_address, index):
        self._root = root
        self._table = table
        self._host_name = host_name
        self._ip_address = ip_address
        self._index = index

        self._my_window: Optional[tk.Toplevel] = None
        self._text = None
        self._vsb = None
        self._check_btn_v = None
        self._check_button = None
        self._data: List[Tuple[str, COLOR]] = []

        self._color = None
        self._statistics = Statistics()
        self._status = CALCULATING
        self._last_status_change = datetime.datetime.now()
        self._is_alive = True
        self._pause = False

    @property
    def _have_window(self):
        return self._my_window is not None

    @property
    def _have_data(self):
        return self._data != []

    @property
    def host_name(self):
        return self._host_name

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def status(self):
        if self._status is not CALCULATING:
            return f'{self._status} since ' + self._last_status_change.strftime('%d.%m.%y %H:%M:%S')
        return CALCULATING

    @status.setter
    def status(self, status):
        if self._status != status:
            self._status = status
            self._last_status_change = datetime.datetime.now()

    @property
    def statistics(self):
        return self._statistics.value

    @property
    def is_alive(self):
        return self._is_alive

    @property
    def values(self):
        return self._index, self._color, self._host_name, self._ip_address, self.status, self.statistics

    @property
    def pause(self):
        return self._pause

    @pause.setter
    def pause(self, pause):
        self._pause = pause

    def add_data(self, data, color):
        if self._have_window:
            self._data.append((data, color))

    def update_line(self, color):
        """
        מעדכן נתונים
        :param color:
        :return:
        """
        self._color = color
        if color == GREEN:
            if self._status == OFFLINE or CALCULATING:
                self.status = ONLINE
            self._statistics += True
        elif color in [RED, YELLOW]:
            if self._status == ONLINE or CALCULATING:
                self.status = OFFLINE
            self._statistics += False
        else:
            self.status = PAUSED

    def create_window(self):
        if not self._have_window:
            self._my_window = tk.Toplevel(self._root)
            self._my_window.geometry('750x250')
            self._my_window.title(f'{self.host_name} ({self.ip_address})')
            self._my_window.protocol('WM_DELETE_WINDOW', self.close_window)

            self._text = tk.Text(self._my_window, height=6, width=40)
            self._vsb = tk.Scrollbar(self._my_window, orient="vertical", command=self._text.yview)
            self._text.configure(yscrollcommand=self._vsb.set)
            self._vsb.pack(side="right", fill="y")
            self._text.pack(side="left", fill="both", expand=True)
            self._check_btn_v = tk.IntVar()
            self._check_button = tk.Checkbutton(self._my_window, text="auto scroll", variable=self._check_btn_v)
            self._check_button.select()
            self._check_button.pack(side=tk.TOP)
        self._my_window.focus_set()

    def close_window(self):
        self._my_window.destroy()
        self._my_window = None
        self._data = []

    def add_data_to_window(self):
        while self._have_data:
            data, color = self._data.pop(0)
            self._text.insert("end", data+'\n')
            if self._check_btn_v.get():
                self._text.see("end")

    def kill(self):
        self._is_alive = False


class IntInputBox(InputBox):
    def __init__(self, master, text, pos, color=BLACK, bg_color=DEF_TEXT_BG_COLOR, size=settings.text_size):
        super(IntInputBox, self).__init__(master, text, pos, color, bg_color, size)
        vcmd = (master.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self._widget.config(validatecommand=vcmd)
        self._changed = True
        self._widget.config(foreground=self._color)

    @staticmethod
    def validate(value_if_allowed):
        if value_if_allowed:
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return True

    @property
    def value(self):
        v = self._widget.get()
        if v:
            return int(v)
        return 0


class SettingsWindow:
    def __init__(self, master, menu):
        self._master = master
        self._menu = menu

        self._my_window = tk.Toplevel(master=master)
        self._my_window.resizable(True, False)
        self._my_window.title('Settings')
        self._my_window.grid_columnconfigure(0, weight=1)
        self._my_window.grid_columnconfigure(1, weight=1)
        self._my_window.grid_rowconfigure(0, weight=1)
        self._my_window.protocol('WM_DELETE_WINDOW', self._close_cmd)

        self._param_frame = tk.Frame(self._my_window, bg=BLACK)
        self._param_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self._param_frame.grid_columnconfigure(0, weight=1)

        self._value_frame = tk.Frame(self._my_window, bg=BLACK)
        self._value_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self._value_frame.grid_columnconfigure(0, weight=1)

        self._items: Dict[str, IntInputBox] = {}
        for i, (key, value) in enumerate(settings.config_params.items()):
            self._param_frame.grid_rowconfigure(i, weight=1)
            self._value_frame.grid_rowconfigure(i, weight=1)

            Text(self._param_frame, key, (i, 0)).draw(padx=2, pady=2, sticky=tk.EW)

            param_value = IntInputBox(self._value_frame, value, (i, 0))
            param_value.draw(padx=2, pady=2, sticky=tk.EW)
            self._items[key] = param_value

        self._buttons_frame = tk.Frame(self._my_window, bg=RED)
        self._buttons_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self._buttons_frame.grid_columnconfigure(0, weight=1)
        self._buttons_frame.grid_columnconfigure(1, weight=1)
        self._buttons_frame.grid_columnconfigure(2, weight=1)

        self._cancel_btn = Button(self._buttons_frame, 'cancel', (0, 0), self._close_cmd)
        self._cancel_btn.draw(sticky=tk.EW)
        self._submit_btn = Button(self._buttons_frame, 'submit', (0, 1), self._submit_cmd)
        self._submit_btn.draw(sticky=tk.EW)
        self._reset_btn = Button(self._buttons_frame, 'reset', (0, 2), self._reset_cmd)
        self._reset_btn.draw(sticky=tk.EW)

    def _close_cmd(self):
        self._menu.window_closed()
        self._my_window.destroy()

    def _submit_cmd(self):
        settings.set_settings({key: value.value for key, value in self._items.items()})
        self._close_cmd()

    def _reset_cmd(self):
        settings.reset_settings()
        self._close_cmd()

    def focus_set(self):
        self._my_window.focus_set()


class Menu:
    def __init__(self, master, table: PingTable):
        self._master = master
        self._table = table

        self._file_name = ''
        self._settings_win: Optional[SettingsWindow] = None

        self._main_menu = tk.Menu(master, tearoff=False)
        self._file_menu = tk.Menu(self._main_menu, tearoff=False)

        self._main_menu.add_cascade(label='file', menu=self._file_menu)

        self._file_menu.add_command(label='open', command=self.open_file_cmd)
        self._file_menu.add_command(label='new', command=self.new_file_cmd)
        self._file_menu.add_separator()
        self._file_menu.add_command(label='save', command=self.save_file_cmd)
        self._file_menu.entryconfig('save', state='normal' if self._file_name else 'disable')
        self._file_menu.add_command(label='save as', command=self.save_as_file_cmd)

        self._main_menu.add_command(label='settings', command=self._open_settings_win)

        master.config(menu=self._main_menu)

    @property
    def file_name(self):
        return self._file_name

    def new_file_cmd(self):
        if ask_for_save(self._table, self):
            self._file_name = ''
            self._table.reset()
            self._file_menu.entryconfig('save', state='disable')

    def open_file_cmd(self):
        if ask_for_save(self._table, self):
            self._file_name = fd.askopenfilename(title='Open File', filetypes=FILE_TYPES, defaultextension='.pngr')
            if self._file_name:
                try:
                    with open(self._file_name, 'r') as my_file:
                        content = my_file.read()
                    content = content.split('\n')[:-1]
                    content = [item.split('->') for item in content]
                    self._table.reset()
                    for item in content:
                        self._table.add(item)
                    self._table.have_changed = False
                    self._file_menu.entryconfig('save', state='normal')
                    return True
                except Exception as e:
                    msgbox.showerror('Error!', f'can\'t open file! {e}')
        return False

    def save_file_cmd(self):
        if self._file_name:
            with open(self._file_name, 'w+') as my_file:
                for host, ip in self._table.items:
                    my_file.write(f'{host}->{ip}\n')
            self._table.have_changed = False
            return True
        return False

    def save_as_file_cmd(self):
        filename = fd.asksaveasfilename(title='Save File', filetypes=FILE_TYPES, defaultextension='.pngr')
        if filename:
            with open(filename, 'w+') as my_file:
                for host, ip in self._table.items:
                    my_file.write(f'{host}->{ip}\n')
            self._file_menu.entryconfig('save', state='normal')
            self._table.have_changed = False
            return True
        return False

    def window_closed(self):
        self._settings_win = None

    def _open_settings_win(self):
        if not self._settings_win:
            self._settings_win = SettingsWindow(self._master, self)
        self._settings_win.focus_set()


class AddDataFrame:
    def __init__(self, master: tk.Misc, pos, table: PingTable):
        self._master = master
        self._pos = pos
        self._table = table
        self._frame = tk.Frame(self._master)
        self._name_input = InputBox(self._frame, 'Host Name', (0, 0))
        self._ip_input = InputBox(self._frame, 'Ip Address', (0, 1))
        self._submit_button = Button(self._frame, 'Submit', (0, 2), self._submit_func)
        for i in range(3):
            self._frame.grid_columnconfigure(i, weight=1)

    def _submit_func(self):
        if self._valid_data:
            self._table.add((self._name_input.value, self._ip_input.value))
            self._master.focus_set()
            self._name_input.reset_text()
            self._ip_input.reset_text()

    def draw(self):
        row, column = self._pos
        self._frame.grid(row=row, column=column, sticky=tk.EW)
        self._name_input.draw(sticky=tk.EW)
        self._ip_input.draw(sticky=tk.EW)
        self._submit_button.draw(sticky=tk.EW)

    @property
    def _valid_data(self):
        if self._name_input.changed and self._name_input.value != '':
            if self._ip_input.changed and self._ip_input.value != '':
                ip = self._ip_input.value
                if valid_ip(ip):
                    return True
                msgbox.showerror('Error!', 'Invalid IP Address!')
                return False
            msgbox.showerror('Error!', 'No IP Address Provided!')
            return False
        msgbox.showerror('Error!', 'No Host Name Provided!')
        return False


def check_keyboard(key_event: tk.Event):
    state = key_event.state
    active_keys = {item: False for item in MODIFIER_KEYS}
    for key, value in MODIFIER_KEYS.items():
        if (state & value) != 0:
            active_keys[key] = True
    return active_keys


def pinger_thread(table_line: PingTableLine):
    ip = table_line.ip_address
    while settings.running and table_line.is_alive:
        output = subprocess.getoutput(f'{settings.ping_command} {ip}')
        output = output.split('\n')[2].lower()
        have_answer = [error_msg for error_msg in ERROR_MSGS if error_msg in output] == []
        if have_answer:
            params = output.split(': ')[1].split(' ')
            items = []
            for item in params:
                if 'bytes' in item or 'ttl' in item:
                    items.append(int(item.split('=')[1]))
                elif 'time' in item:
                    items.append(int(item.split('=' if '=' in item else '<')[1].strip('ms')))
            p_bytes, p_time, p_ttl = items
            color = YELLOW if p_time < DOCK_PARAM else GREEN
        else:
            color = RED
        time_str = datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')
        table_line.add_data(f'{time_str} -> {output}', color)
        table_line.update_line(color)
        time.sleep(settings.ping_sleep_timer)
        while table_line.pause and settings.running and table_line.is_alive:
            color = GRAY
            table_line.update_line(color)
            time.sleep(settings.ping_sleep_timer)


def valid_ip(ip):
    ip = ip.split('.')
    if len(ip) != 4:
        return False
    try:
        for item in ip:
            if not 0 <= int(item) <= 255:
                return False
        return True
    except ValueError:
        return False


def ask_for_save(table, main_menu):
    if table.have_changed:
        msg_box = msgbox.askyesnocancel('Save Changes', 'Do you want to save changes?')
        if msg_box in [True, False]:
            if msg_box is True:
                if main_menu.file_name:
                    main_menu.save_file_cmd()
                else:
                    if not main_menu.save_as_file_cmd():
                        return False
        else:
            return False
    return True


def do_quit(root, table, main_menu):
    if ask_for_save(table, main_menu):
        settings.running = False
        table.join()
        root.destroy()


def init_root():
    root = tk.Tk()
    # root.geometry(SCREEN_SIZE)
    root.title(SCREEN_TITLE)
    root.grid_columnconfigure(0, weight=1)
    return root


def main():
    root = init_root()
    settings.add_root(root)
    table = PingTable(root, (1, 0))
    # for i in range(255):
    #     table.add(('hi', f'{i}.{i}.{i}.{i}'))
    main_menu = Menu(root, table)
    add_data_frame = AddDataFrame(root, (0, 0), table)
    add_data_frame.draw()
    blank_frame = tk.Frame(root)
    blank_frame.grid(row=2, column=0)
    tk.Label(blank_frame, text='').pack()
    credit_label = tk.Label(root, text='Pinger++ by Yuval Kalanthroff', bd=1, relief=tk.SUNKEN)
    credit_label.place(relx=0.5, rely=1.0, anchor='s', relwidth=1.0)
    root.protocol('WM_DELETE_WINDOW', lambda: do_quit(root, table, main_menu))
    tk.mainloop()


if __name__ == '__main__':
    main()
