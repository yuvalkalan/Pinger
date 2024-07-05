from constants import *
from tkinter import filedialog as fd, messagebox as msgbox, ttk
from typing import List, Optional, Dict
import datetime
import threading
import time
import subprocess
import tkinter as tk


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
        self._ping_df_flag = None
        self._ping_ttl = None
        self._scroll_sensitivity = None
        self._statistics_capacity = None
        self._num_of_tables = self._original_num_of_tables = None
        self._dock_time = None
        self.config_params = self._read_settings_file()
        self._original_num_of_tables = self._num_of_tables

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
        self._table_adder = (self._table_adder + 1) % self._original_num_of_tables
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
                    try:
                        items[key] = int(value)
                    except ValueError:
                        items[key] = float(value)
        except (OSError, ValueError):
            items = DEFAULT_SETTINGS
        return items

    def set_settings(self, new_settings):
        self.config_params = new_settings
        with open(SETTINGS_FILE, 'w+') as my_file:
            text = '\n'.join([f'{key}={value}' for key, value in self.config_params.items()])
            my_file.write(text)

    def reset_settings(self):
        self.set_settings(DEFAULT_SETTINGS)

    def _set_config(self):
        self._tree_head_stl = ttk.Style()
        self._tree_head_stl.configure("Treeview.Heading",
                                      font=(DEF_TEXT_FONT, self.text_size * TEXT_HEAD_RATIO, 'bold'))

        self._tree_body_stl = ttk.Style()
        self._tree_body_stl.configure("Treeview", font=(DEF_TEXT_FONT, self.text_size, 'bold'),
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
    def ping_df_flag(self):
        return self._ping_df_flag

    @property
    def ping_ttl(self):
        return self._ping_ttl

    @property
    def scroll_sensitivity(self):
        return self._scroll_sensitivity

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
    def num_of_tables(self):
        return self._num_of_tables

    @property
    def dock_time(self):
        return self._dock_time

    @property
    def config_params(self):
        return {Config.TEXT_SIZE: self.text_size,
                Config.SLEEP_TIMER: self.ping_sleep_timer,
                Config.TIMEOUT: self.ping_timeout,
                Config.BUFFER_SIZE: self.ping_buffer_size,
                Config.DF_FLAG: self.ping_df_flag,
                Config.TTL: self.ping_ttl,
                Config.SCROLL_SENSITIVITY: self.scroll_sensitivity,
                Config.STATISTICS_CAPACITY: self.statistics_capacity,
                Config.NUM_OF_TABLES: self.num_of_tables,
                Config.DOCK_TIME: self.dock_time}

    @config_params.setter
    def config_params(self, config_params):
        self._text_size = config_params[Config.TEXT_SIZE]
        self._ping_sleep_timer = config_params[Config.SLEEP_TIMER]
        self._ping_timeout = config_params[Config.TIMEOUT]
        self._ping_buffer_size = config_params[Config.BUFFER_SIZE]
        self._ping_df_flag = config_params[Config.DF_FLAG]
        self._ping_ttl = config_params[Config.TTL]
        self._scroll_sensitivity = config_params[Config.SCROLL_SENSITIVITY]
        self._statistics_capacity = config_params[Config.STATISTICS_CAPACITY]
        self._num_of_tables = config_params[Config.NUM_OF_TABLES]
        self._dock_time = config_params[Config.DOCK_TIME]
        if self._root:
            self._set_config()

    def add_root(self, root):
        self._root = root
        self._set_config()


settings = Settings()


class Text:
    def __init__(self, master, text, pos, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR,
                 size=Default.TEXT_SIZE.value):
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
                 size=Default.TEXT_SIZE.value):
        super(Button, self).__init__(master, text, pos, color, bg_color, size)
        self._func = func
        self._widget = tk.Button(master, text=text, fg=color, bg=bg_color, command=func, font=self._font)


class InputBox(Text):
    def __init__(self, master, text, pos, color=Color.BLACK, bg_color=DEF_TEXT_BG_COLOR, size=Default.TEXT_SIZE.value):
        super(InputBox, self).__init__(master, text, pos, color, bg_color, size)
        self._widget = tk.Entry(master, fg=Color.GRAY, bg=bg_color, font=self._font)
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
        self._widget.config(foreground=Color.GRAY)
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
        master.grid_columnconfigure(column, weight=1)
        self._master = master
        self._frame = tk.Frame(master)
        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid(row=row, column=column, sticky=tk.NSEW)
        # create tree
        self._tree = ttk.Treeview(self._frame, columns=titles, show='headings')
        for column in titles:
            self._tree.heading(column, text=column)
            self._tree.column(column, minwidth=0)
        self._tree.grid(row=0, column=0, sticky=tk.NSEW)
        # add a scrollbar
        self._scrollbar = ttk.Scrollbar(self._frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.grid(row=0, column=1, sticky='ns')
        self._menu = tk.Menu(self._frame, tearoff=False)
        self._menu.add_command(label='remove', command=self._remove_cmd)
        self._menu.add_command(label='forward', command=self._forward_cmd)
        self._menu.add_command(label='backward', command=self._backward_cmd)
        self._tree.bind('<Button-3>', self._popup_menu)
        self._tree.bind('<FocusOut>', lambda e: self._tree.selection_set([]))

        self._have_changed = False

    @property
    def have_changed(self):
        return self._have_changed

    @have_changed.setter
    def have_changed(self, value):
        self._have_changed = value

    @property
    def children(self):
        return self._tree.get_children()

    @property
    def selection(self):
        return self._tree.selection()

    def _popup_menu(self, event):
        iids = self.selection
        children = self.children
        first, last = children[0], children[-1]
        self._menu.entryconfig('forward', state='disable' if first in iids else 'normal')
        self._menu.entryconfig('backward', state='disable' if last in iids else 'normal')
        self._menu.tk_popup(event.x_root, event.y_root)

    def _remove_cmd(self):
        for iid in self.selection:
            self._tree.delete(iid)

    def _switch_pos(self, first, second):
        children = self.children
        first_row, second_row = self._tree.item(first), self._tree.item(second)
        first_value, first_tag = first_row['values'], first_row['tags']
        second_value, second_tag = second_row['values'], second_row['tags']
        self._tree.delete(first)
        self._tree.insert('', children.index(first), iid=first, values=second_value, tags=second_tag)
        self._tree.delete(second)
        self._tree.insert('', children.index(second), iid=second, values=first_value, tags=first_tag)

    def _forward_cmd(self):
        iids = self.selection
        children = self.children
        new = []
        if iids:
            self._have_changed = True
        for iid in iids:
            for i, child in enumerate(children):
                if iid == child:
                    new.append(children[i - 1])
                    self._switch_pos(child, children[i-1])
        self._tree.selection_set(new)

    def _backward_cmd(self):
        iids = self.selection[::-1]
        children = self.children
        new = []
        if iids:
            self._have_changed = True
        for iid in iids:
            for i, child in enumerate(children):
                if iid == child:
                    new.append(children[i + 1])
                    self._switch_pos(child, children[i + 1])
        self._tree.selection_set(new)

    def add(self, line):
        return self._tree.insert('', tk.END, values=line)


class PingTable(Table):
    def __init__(self, master: tk.Misc, pos, tables, table_index):
        super(PingTable, self).__init__(master, ('Host Name', 'Ip Address', 'Status', 'Statistics (%)'), pos)
        self._master.after(100, self._check_pingers)
        self._tables: List[PingTable] = tables
        self._table_index = table_index
        self._ping_threads: List[threading.Thread] = []
        self._item_indexes: Dict[str, PingTableLine] = {}

        self._tree.tag_configure(Color.GREEN, background=Color.GREEN)
        self._tree.tag_configure(Color.YELLOW, background=Color.YELLOW)
        self._tree.tag_configure(Color.RED, background=Color.RED)
        self._tree.tag_configure(Color.GRAY, background=Color.GRAY)
        self._tree.bind('<Double-Button-1>', self._open_sub_window)
        self._tree.bind('<KeyPress>', self._check_keypress)

        self._menu.add_command(label='pause/resume', command=self._pause_cmd)
        self._menu.add_command(label='edit', command=self._edit_cmd)
        self._menu.add_command(label='move table', command=self._move_table_cmd)

    def _popup_menu(self, event):
        iids = self.selection
        self._menu.entryconfig('edit', state='disable' if len(iids) != 1 else 'normal')
        super(PingTable, self)._popup_menu(event)

    def _pause_cmd(self):
        for iid in self.selection:
            self._item_indexes[iid].pause = not self._item_indexes[iid].pause

    def _edit_cmd(self):
        EditRow(self._master, self._item_indexes[self.selection[0]])
        self._have_changed = True

    def _move_table_cmd(self):
        for item in self.selection:
            line = self._item_indexes[item]
            self._tables[(self._table_index + 1) % len(self._tables)].add((line.host_name, line.ip_address))
        self._remove_cmd()

    def _remove_cmd(self):
        for iid in self.selection:
            self._tree.delete(iid)
            self._item_indexes.pop(iid).kill()
        self._have_changed = True

    def _switch_pos(self, first, second):
        super(PingTable, self)._switch_pos(first, second)
        first_row, second_row = self._item_indexes[first], self._item_indexes[second]
        first_row.iid, second_row.iid = second_row.iid, first_row.iid
        self._item_indexes[first], self._item_indexes[second] = second_row, first_row

    def _open_sub_window(self, event: tk.Event):
        pressed_keys = check_keyboard(event)
        if not pressed_keys[Modifiers.CTRL]:
            iids = self.selection
            if len(iids) == 1:
                line = self._item_indexes[iids[0]]
                line.create_window()

    def _check_keypress(self, event: tk.Event):
        pressed_keys = check_keyboard(event)
        keycode = event.keycode
        match keycode:
            case Keycodes.A:
                if pressed_keys[Modifiers.CTRL]:
                    self._tree.selection_set(self.children)
            case Keycodes.ESCAPE:
                self._tree.selection_set([])
            case Keycodes.DELETE:
                self._remove_cmd()
            case Keycodes.UP | Keycodes.DOWN:
                selection = [item for item in self.selection]
                if selection:
                    if pressed_keys[Modifiers.SHIFT]:
                        if keycode == Keycodes.UP and self.children[0] not in selection:
                            self._forward_cmd()
                        elif keycode == Keycodes.DOWN and self.children[-1] not in selection:
                            self._backward_cmd()
                    else:
                        children = self.children
                        top_most = selection[0]
                        for i, child in enumerate(children):
                            if child == top_most:
                                direction = -1 if keycode == Keycodes.UP else 1
                                self._tree.selection_set(children[(i + direction) % len(children)])
                                break
            case _:
                print(event)

    def add(self, host_name_and_ip_address):
        name, ip = host_name_and_ip_address
        if name and ip:
            iid = super(PingTable, self).add([name, ip, Status.CALCULATING, '?%'])
            new_line = PingTableLine(self._master, self, name, ip, iid)
            self._item_indexes[iid] = new_line

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
        for i in self.children:
            self._tree.delete(i)
        self._item_indexes = {}

    def _submit_updates(self, iid, color, name, ip, status, statistics):
        children = self.children
        self._tree.delete(iid)
        self._tree.insert('', children.index(iid), iid=iid, values=[name, ip, status, statistics], tags=[color])

    def _check_pingers(self):
        selections = self.selection
        for iid in self._item_indexes:
            line = self._item_indexes[iid]
            self._submit_updates(*line.values)
            line.add_data_to_window()
        self._tree.selection_set(selections)
        self._master.after(int(500 * settings.ping_sleep_timer), self._check_pingers)

    @property
    def items(self):
        return [(line.host_name, line.ip_address) for line in self._item_indexes.values()]


class Statistics:
    def __init__(self):
        self._values = []
        self._index = 0
        self._capacity = settings.statistics_capacity

    def __iadd__(self, other):
        value = 1 if other else 0
        if self._capacity_changed:
            self._values = []
            self._index = 0
        if len(self._values) < self._capacity:
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

    @property
    def _capacity_changed(self):
        value = self._capacity != settings.statistics_capacity
        self._capacity = settings.statistics_capacity
        return value


class PingTableLine:
    def __init__(self, root, table, host_name, ip_address, iid):
        self._root = root
        self._table = table
        self._host_name = host_name
        self._ip_address = ip_address
        self._iid = iid

        self._my_window: Optional[tk.Toplevel] = None
        self._text: Optional[tk.Text] = None
        self._vsb = None
        self._check_btn_v = None
        self._check_button = None
        self._data: List[Tuple[str, COLOR]] = []

        self._color = None
        self._statistics = Statistics()
        self._status = Status.CALCULATING
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

    @host_name.setter
    def host_name(self, value):
        self._host_name = value

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value
        self._color = None
        self._statistics = Statistics()
        self._status = Status.CALCULATING
        self._last_status_change = datetime.datetime.now()

    @property
    def status(self):
        if self._status is not Status.CALCULATING:
            return f'{self._status} since ' + self._last_status_change.strftime('%d.%m.%y %H:%M:%S')
        return Status.CALCULATING

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
        return self._iid, self._color, self._host_name, self._ip_address, self.status, self.statistics

    @property
    def pause(self):
        return self._pause

    @pause.setter
    def pause(self, pause):
        self._pause = pause

    @property
    def iid(self):
        return self._iid

    @iid.setter
    def iid(self, iid):
        self._iid = iid

    def add_data(self, data, color):
        if self._have_window:
            self._data.append((data, color))

    def update_line(self, color):
        """
        change line params
        :param color:
        :return:
        """
        self._color = color
        if color == Color.GREEN:
            if self._status == Status.OFFLINE or Status.CALCULATING:
                self.status = Status.ONLINE
            self._statistics += True
        elif color in [Color.RED, Color.YELLOW]:
            if self._status == Status.ONLINE or Status.CALCULATING:
                self.status = Status.OFFLINE
            self._statistics += False
        else:
            self.status = Status.PAUSED

    def create_window(self):
        if not self._have_window:
            self._my_window = tk.Toplevel(self._root)
            self._my_window.geometry('750x250')
            self._my_window.title(f'{self.host_name} ({self.ip_address})')
            self._my_window.protocol('WM_DELETE_WINDOW', self.close_window)

            self._text = tk.Text(self._my_window, height=6, width=40)
            self._text.tag_config(Color.RED, background=Color.RED)
            self._text.tag_config(Color.YELLOW, background=Color.YELLOW)
            self._text.tag_config(Color.GREEN, background=Color.GREEN)
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
            self._text.insert(tk.END, data+'\n', color)
            if self._check_btn_v.get():
                self._text.see(tk.END)

    def kill(self):
        self._is_alive = False


class EditRow:
    def __init__(self, master, line: PingTableLine):
        self._master = master
        self._line = line

        self._my_window = tk.Toplevel(self._master)
        self._my_window.title(f'edit {line.host_name} ({line.ip_address})')
        self._my_window.wm_minsize(150, 50)
        self._my_window.grid_rowconfigure(0, weight=1)
        self._my_window.grid_rowconfigure(1, weight=1)
        self._my_window.grid_columnconfigure(0, weight=1)
        self._my_window.grid_columnconfigure(1, weight=1)

        self._name_input = InputBox(self._my_window, 'Host Name', (0, 0))
        self._name_input.draw(sticky=tk.NSEW)
        self._ip_input = InputBox(self._my_window, 'Ip Address', (0, 1))
        self._ip_input.draw(sticky=tk.NSEW)
        self._submit_btn = Button(self._my_window, 'submit', (1, 0), self._edit_cmd)
        self._submit_btn.draw(columnspan=2, sticky=tk.NSEW)

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

    def _edit_cmd(self):
        if self._valid_data:
            self._line.host_name, self._line.ip_address = self._name_input.value, self._ip_input.value
            self._my_window.destroy()


class FloatInputbox(InputBox):
    def __init__(self, master, text, pos, color=Color.BLACK, bg_color=DEF_TEXT_BG_COLOR, size=Default.TEXT_SIZE.value):
        super(FloatInputbox, self).__init__(master, text, pos, color, bg_color, size)
        validate_cmd = (master.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self._widget.config(validate='key', validatecommand=validate_cmd)
        self._changed = True
        self._widget.config(foreground=self._color)

    @staticmethod
    def validate(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                float(value_if_allowed)
            except ValueError:
                return False
        return True

    @property
    def value(self):
        v = self._widget.get()
        if v:
            return float(v)
        return None


class IntInputBox(FloatInputbox):
    def __init__(self, master, text, pos, color=Color.BLACK, bg_color=DEF_TEXT_BG_COLOR, size=Default.TEXT_SIZE.value):
        super(IntInputBox, self).__init__(master, text, pos, color, bg_color, size)

    @staticmethod
    def validate(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            try:
                int(value_if_allowed)
            except ValueError:
                return False
        return True

    @property
    def value(self):
        v = self._widget.get()
        if v:
            return int(v)
        return None


class BoolInputBox(IntInputBox):
    def __init__(self, master, text, pos, color=Color.BLACK, bg_color=DEF_TEXT_BG_COLOR, size=Default.TEXT_SIZE.value):
        super(IntInputBox, self).__init__(master, text, pos, color, bg_color, size)

    @staticmethod
    def validate(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed:
            if value_if_allowed.lower() not in ['t', 'f']:
                return False
        return True

    @property
    def value(self):
        v = self._widget.get()
        if v:
            return 1 if v.lower() == 't' else 0
        return None


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
        self._my_window.bind('<Return>', self._submit_cmd)
        self._my_window.bind('<Escape>', self._close_cmd)
        self._my_window.bind('<Delete>', self._reset_cmd)

        self._param_frame = tk.Frame(self._my_window, bg=Color.BLACK)
        self._param_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self._param_frame.grid_columnconfigure(0, weight=1)

        self._value_frame = tk.Frame(self._my_window, bg=Color.BLACK)
        self._value_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self._value_frame.grid_columnconfigure(0, weight=1)

        self._items: Dict[str, FloatInputbox] = {}
        for i, (key, value) in enumerate(settings.config_params.items()):
            self._param_frame.grid_rowconfigure(i, weight=1)
            self._value_frame.grid_rowconfigure(i, weight=1)

            Text(self._param_frame, key, (i, 0)).draw(padx=2, pady=2, sticky=tk.EW)
            if key in [Config.TIMEOUT, Config.SLEEP_TIMER]:
                param_value = FloatInputbox(self._value_frame, value, (i, 0))
            elif key in [Config.DF_FLAG]:
                param_value = BoolInputBox(self._value_frame, 'T' if value else 'F', (i, 0))
            else:
                param_value = IntInputBox(self._value_frame, value, (i, 0))
            param_value.draw(padx=2, pady=2, sticky=tk.EW)
            self._items[key] = param_value

        self._buttons_frame = tk.Frame(self._my_window, bg=Color.RED)
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

    def _close_cmd(self, *_):
        self._menu.window_closed()
        self._my_window.destroy()

    def _submit_cmd(self, *_):
        new_settings = {key: value.value for key, value in self._items.items()}
        for key in new_settings:
            if new_settings[key] is None:
                new_settings[key] = DEFAULT_SETTINGS[key]
        settings.set_settings(new_settings)
        self._close_cmd()

    def _reset_cmd(self, *_):
        settings.reset_settings()
        self._close_cmd()

    def focus_set(self):
        self._my_window.focus_set()


class Menu:
    def __init__(self, master, tables: List[PingTable]):
        self._master = master
        self._tables = tables

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
        if ask_for_save(self._tables, self):
            self._file_name = ''
            for table in self._tables:
                table.reset()
            settings.reset_adder()
            self._file_menu.entryconfig('save', state='disable')
            self._master.title(DEF_SCREEN_TITLE)

    def open_file_cmd(self, filename=''):
        last_file_name = self._file_name
        if ask_for_save(self._tables, self):
            if filename:
                self._file_name = filename
            else:
                self._file_name = fd.askopenfilename(title='Open File', filetypes=FILE_TYPES, defaultextension='.pngr')
            if self._file_name:
                try:
                    with open(self._file_name, 'r') as my_file:
                        content = my_file.read()
                    content = content.split('\n')[:-1]
                    content = [item.split('->') for item in content]
                    for item in content:
                        if len(item) != 2:
                            raise ValueError
                    for table in self._tables:
                        table.reset()
                    settings.reset_adder()
                    for item in content:
                        self._tables[settings.table_adder].add(item)
                    for table in self._tables:
                        table.have_changed = False
                    self._file_menu.entryconfig('save', state='normal')
                    self._master.title(f'{self._file_name} - pinger++')
                    return True
                except Exception as e:
                    msgbox.showerror('Error!', f'can\'t open file! {e}')
                    self._file_name = last_file_name
        return False

    def save_file_cmd(self):
        if self._file_name:
            with open(self._file_name, 'w+') as my_file:
                table_items = [table.items for table in self._tables]
                max_len = len(max(table_items, key=len))
                for items in table_items:
                    while len(items) != max_len:
                        items.append(('', ''))
                items = []
                for item_group in zip(*table_items):
                    for item in item_group:
                        items.append(item)
                for host, ip in items:
                    my_file.write(f'{host}->{ip}\n')
            for table in self._tables:
                table.have_changed = False
            return True
        return False

    def save_as_file_cmd(self):
        self._file_name = fd.asksaveasfilename(title='Save File', filetypes=FILE_TYPES, defaultextension='.pngr')
        if self.save_file_cmd():
            self._master.title(f'{self._file_name} - pinger++')
            self._file_menu.entryconfig('save', state='normal')
            return True
        return False

    def window_closed(self):
        self._settings_win = None

    def _open_settings_win(self):
        if not self._settings_win:
            self._settings_win = SettingsWindow(self._master, self)
        self._settings_win.focus_set()


class AddDataFrame:
    def __init__(self, master: tk.Misc, pos, tables: List[PingTable]):
        self._master = master
        self._pos = pos
        self._tables = tables
        self._frame = tk.Frame(self._master)
        self._name_input = InputBox(self._frame, 'Host Name', (0, 0))
        self._ip_input = InputBox(self._frame, 'Ip Address', (0, 1))
        self._submit_button = Button(self._frame, 'Submit', (0, 2), self._submit_func)
        for i in range(3):
            self._frame.grid_columnconfigure(i, weight=1)
        row, column = self._pos
        self._frame.grid(row=row, column=column, sticky=tk.EW, columnspan=settings.num_of_tables)
        self._name_input.draw(sticky=tk.EW)
        self._ip_input.draw(sticky=tk.EW)
        self._submit_button.draw(sticky=tk.EW)

    def _submit_func(self):
        if self._valid_data:
            self._tables[settings.table_adder].add((self._name_input.value, self._ip_input.value))
            self._master.focus_set()
            self._name_input.reset_text()
            self._ip_input.reset_text()

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


def pinger_thread(table_line: PingTableLine):
    while settings.running and table_line.is_alive:
        ip = table_line.ip_address
        try:
            output = subprocess.getoutput(f'{settings.ping_command} {ip}')
            output = output.split('\n')[2].lower()
            have_answer = [error_msg for error_msg in ERROR_MSGS if error_msg in output] == []
        except Exception as e:
            have_answer = False
            output = str(e)
        if have_answer:
            params = output.split(': ')[1].split(' ')
            items = []
            for item in params:
                if 'bytes' in item or 'ttl' in item:
                    items.append(int(item.split('=')[1]))
                elif 'time' in item:
                    items.append(int(item.split('=' if '=' in item else '<')[1].strip('ms')))
            p_bytes, p_time, p_ttl = items
            color = Color.YELLOW if p_time < settings.dock_time else Color.GREEN
        else:
            color = Color.RED
        time_str = datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')
        table_line.add_data(f'{time_str} -> {output}', color)
        table_line.update_line(color)
        time.sleep(settings.ping_sleep_timer)
        while table_line.pause and settings.running and table_line.is_alive:
            color = Color.GRAY
            table_line.update_line(color)
            time.sleep(settings.ping_sleep_timer)


def ask_for_save(tables, main_menu):
    if [table for table in tables if table.have_changed]:
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


def check_keyboard(key_event: tk.Event):
    state = key_event.state
    active_keys = {item: False for item in MODIFIER_KEYS}
    for key, value in MODIFIER_KEYS.items():
        if (state & value) != 0:
            active_keys[key] = True
    return active_keys
