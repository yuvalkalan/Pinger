from font import *
from tkinter import filedialog as fd, messagebox as msgbox, ttk
import threading
import time
from ping import PingSocket


class PingTable(Table):
    def __init__(self, master: tk.PanedWindow, pos, tables, table_index):
        super(PingTable, self).__init__(master, ('(%) סטטיסטיקה', 'סטטוס', 'כתובת היעד', 'שם היעד'), pos)
        self._master.after(0, self._check_pingers)
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
        key_code = event.keycode
        if key_code == Keycodes.A:
            if pressed_keys[Modifiers.CTRL]:
                self._tree.selection_set(self.children)
        elif key_code == Keycodes.ESCAPE:
            self._tree.selection_set([])
        elif key_code == Keycodes.DELETE:
            self._remove_cmd()
        elif key_code in [Keycodes.UP, Keycodes.DOWN]:
            selection = [item for item in self.selection]
            if selection:
                if pressed_keys[Modifiers.SHIFT]:
                    if key_code == Keycodes.UP and self.children[0] not in selection:
                        self._forward_cmd()
                    elif key_code == Keycodes.DOWN and self.children[-1] not in selection:
                        self._backward_cmd()
                else:
                    children = self.children
                    top_most = selection[0]
                    for i, child in enumerate(children):
                        if child == top_most:
                            direction = -1 if key_code == Keycodes.UP else 1
                            new_selection = children[(i + direction) % len(children)]
                            self._tree.selection_set(new_selection)
                            self._tree.see(new_selection)
                            break

    def add(self, host_and_ip_address):
        name, ip = host_and_ip_address
        if name and ip:
            iid = super(PingTable, self).add(['?%', Status.CALCULATING, ip, hebrew_reshaper(name)])
            new_line = PingTableLine(self._master, self, name, ip, iid)
            self._item_indexes[iid] = new_line

            self._have_changed = True
            thread = threading.Thread(target=pinger_thread,
                                      args=[new_line, (self._table_index+1) * 1000 + len(self._ping_threads)])
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
        name = hebrew_reshaper(name)
        self._tree.insert('', children.index(iid), iid=iid, values=[statistics, status, ip, name], tags=[color])

    def _check_pingers(self):
        log.update()
        selection = self.selection
        for iid in self._item_indexes:
            line = self._item_indexes[iid]
            self._submit_updates(*line.values)
            line.add_data_to_window()
        self._tree.selection_set(selection)
        self._master.after(settings.ping_sleep_timer, self._check_pingers)

    @property
    def items(self):
        return [(line.host_name, line.ip_address) for line in self._item_indexes.values()]

    def move_table_cmd(self):
        self._tree.selection_set(self.children)
        self._move_table_cmd()


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

    def __float__(self):
        return round((sum(self._values) / len(self._values)), 2)

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


class ColorMaster:
    def __init__(self):
        self._log_line = None
        self._last_colors = [None] * 2   # len(last_colors) = amount of values to consider change (remove jitters)
        self._last_change_color = None

    def update(self, color):
        self.color = color
        log_line = None
        if self._is_changed:
            if self._last_change_color and self.color:
                log_line = LOG_MODES[self._last_change_color][self._last_colors[-1]]
            self._last_change_color = self.color
        return log_line

    @property
    def color(self):
        return self._last_colors[-1]

    @color.setter
    def color(self, color):
        # add the new color to the last_colors list and remove the last color
        self._last_colors = (self._last_colors[1:] + [color])

    @property
    def _is_changed(self):
        # if all last_colors are the same
        if all(color == self._last_colors[0] for color in self._last_colors):
            # check if they different from the last_change_color
            return self._last_colors[0] != self._last_change_color
        return False


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

        self._color = ColorMaster()
        self._statistics = Statistics()
        self._status = Status.CALCULATING
        self._last_status_change = None
        self._is_alive = True
        self._pause = False
        self._read_start_pos()

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
        self._color = ColorMaster()
        self._statistics = Statistics()
        self._status = Status.CALCULATING
        self._last_status_change = None

    @property
    def status(self):
        if not self._last_status_change:
            return '--.-- --:--'
        if self._status is Status.CALCULATING:
            return Status.CALCULATING
        return self._last_status_change.strftime('%d.%m %H:%M')

    @status.setter
    def status(self, status):
        if not self._last_status_change and status is Status.OFFLINE:
            return
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
        return self._iid, self._color.color, self._host_name, self._ip_address, self.status, self.statistics

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
        # add line to log
        log_mode = self._color.update(color)
        if log_mode and not (settings.log_ignore_dock and log_mode in [LOG_MODE_Y2R, LOG_MODE_R2Y]):
            log.add(self.host_name, log_mode)
        # change color and status
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
            self._my_window.title(f'({self.ip_address}) {hebrew_reshaper(self.host_name)}')
            self._my_window.protocol('WM_DELETE_WINDOW', self.close_window)

            self._text = tk.Text(self._my_window, height=6, width=40)
            self._text.tag_config(Color.RED, background=Color.RED)
            self._text.tag_config(Color.YELLOW, background=Color.YELLOW)
            self._text.tag_config(Color.GREEN, background=Color.GREEN)
            self._vsb = tk.Scrollbar(self._my_window, orient='vertical', command=self._text.yview)
            self._text.configure(yscrollcommand=self._vsb.set)
            self._vsb.pack(side='right', fill='y')
            self._text.pack(side='left', fill='both', expand=True)
            self._check_btn_v = tk.IntVar()
            self._check_button = tk.Checkbutton(self._my_window, text='auto scroll', variable=self._check_btn_v)
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
            self._text.insert(tk.END, data + '\n', color)
            if self._check_btn_v.get():
                self._text.see(tk.END)

    def kill(self):
        self._is_alive = False

    def _read_start_pos(self):
        if self._host_name in log.start_pos:
            time_stamp, value = log.start_pos[self._host_name]
            if value in [LOG_MODE_R2G, LOG_MODE_Y2G]:
                self._status = Status.ONLINE
            else:
                self._status = Status.OFFLINE
            self._last_status_change = time_stamp


class EditRow:
    def __init__(self, master, line: PingTableLine):
        self._master = master
        self._line = line

        self._my_window = tk.Toplevel(self._master)
        self._my_window.title(f'edit {line.host_name}, ({line.ip_address})')
        self._my_window.wm_minsize(150, 50)
        self._my_window.grid_rowconfigure(0, weight=1)
        self._my_window.grid_rowconfigure(1, weight=1)
        self._my_window.grid_columnconfigure(0, weight=1)
        self._my_window.grid_columnconfigure(1, weight=1)

        self._name_input = Inputbox(self._my_window, 'Host Name', (0, 0))
        self._name_input.draw(sticky=tk.NSEW)
        self._ip_input = Inputbox(self._my_window, 'Ip Address', (0, 1))
        self._ip_input.draw(sticky=tk.NSEW)
        self._submit_btn = Button(self._my_window, 'submit', (1, 0), self._edit_cmd)
        self._submit_btn.draw(columnspan=2, sticky=tk.NSEW)

    @property
    def _valid_data(self):
        if self._name_input.changed and self._name_input.value != '':
            if len(self._name_input.value) >= MAX_SUBJECT_LENGTH - 2:
                msgbox.showerror('Error!', f'Host Name is Longer then {MAX_SUBJECT_LENGTH - 2} Chars!')
                return False
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


class SettingsWindow:
    def __init__(self, master, menu):
        self._master = master
        self._menu = menu

        self._my_window = tk.Toplevel(master)
        self._my_window.resizable(True, False)
        self._my_window.title('Settings')
        self._my_window.grid_columnconfigure(0, weight=1)
        self._my_window.grid_columnconfigure(1, weight=1)
        self._my_window.grid_rowconfigure(0, weight=1)
        self._my_window.protocol('WM_DELETE_WINDOW', self._close_cmd)
        self._my_window.bind('<Return>', self._submit_cmd)
        self._my_window.bind('<Escape>', self._close_cmd)

        self._start_values = settings.config_params

        self._param_frame = tk.Frame(self._my_window, bg=Color.BLACK)
        self._param_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self._param_frame.grid_columnconfigure(0, weight=1)

        self._value_frame = tk.Frame(self._my_window, bg=Color.BLACK)
        self._value_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self._value_frame.grid_columnconfigure(0, weight=1)

        self._items: Dict[str, FloatInputBox] = {}
        for i, (key, value) in enumerate(settings.config_params.items()):
            self._param_frame.grid_rowconfigure(i, weight=1)
            self._value_frame.grid_rowconfigure(i, weight=1)

            Text(self._param_frame, key, (i, 0)).draw(padx=2, pady=2, sticky=tk.EW)
            if key in [Config.LOG_IGNORE_DOCK]:
                param_value = BoolInputBox(self._value_frame, str(bool(value)), (i, 0))
            else:
                from_, to = RANGE_OF_SETTINGS[key]
                if key in [Config.TEXT_SIZE]:
                    param_value = IntInputBox(self._value_frame, value, (i, 0), from_, to,
                                              on_change=self._set_text_size)
                else:
                    param_value = IntInputBox(self._value_frame, value, (i, 0), from_, to)
            param_value.draw(padx=2, pady=2, sticky=tk.EW)
            self._items[key] = param_value

        self._buttons_frame = tk.Frame(self._my_window)
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
        settings.config_params = self._start_values
        self._on_exit()

    def _submit_cmd(self, *_):
        new_settings = {key: value.value for key, value in self._items.items()}
        for key in new_settings:
            if new_settings[key] is None:
                new_settings[key] = DEFAULT_SETTINGS[key]
        self._menu.set_num_of_table(new_settings[Config.NUM_OF_TABLES])
        settings.set_settings(new_settings)
        self._on_exit()

    def _reset_cmd(self, *_):
        settings.reset_settings()
        self._on_exit()

    def _on_exit(self):
        self._menu.settings_closed()
        self._my_window.destroy()

    def _set_text_size(self):
        settings.set_text_size(self._items[Config.TEXT_SIZE].value)

    def focus_set(self):
        self._my_window.focus_set()


class AutoInsertWin:
    def __init__(self, master, menu, num_of_tables):
        self._master = master
        self._menu = menu

        self._my_window = tk.Toplevel(master)
        self._my_window.resizable(True, False)
        self._my_window.title('Auto Insert')
        self._my_window.protocol('WM_DELETE_WINDOW', self._close_cmd)
        self._my_window.grid_columnconfigure(0, weight=1)
        self._my_window.grid_rowconfigure(0, weight=1)

        self._main_frame = tk.Frame(self._my_window, bg=Color.BLACK)
        self._main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        for i in range(4):
            self._main_frame.grid_columnconfigure(i, weight=1)

        self._title = Text(self._main_frame, 'Enter IP Range:', (0, 0))
        self._title.draw(sticky=tk.EW, columnspan=4)

        self._start_ip = [IntInputBox(self._main_frame, '0', (1, i), 0, 255) for i in range(4)]
        for box in self._start_ip:
            box.draw(sticky=tk.EW, padx=2, pady=2)

        self._end_ip = [IntInputBox(self._main_frame, '255', (2, i), 0, 255) for i in range(4)]
        for box in self._end_ip:
            box.draw(sticky=tk.EW, padx=2, pady=2)

        self._buttons_frame = tk.Frame(self._my_window)
        self._buttons_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self._buttons_frame.grid_columnconfigure(0, weight=1)
        self._buttons_frame.grid_columnconfigure(1, weight=1)
        self._buttons_frame.grid_columnconfigure(2, weight=1)

        self._cancel_btn = Button(self._buttons_frame, 'cancel', (0, 0), self._close_cmd)
        self._cancel_btn.draw(sticky=tk.EW)
        self._submit_btn = Button(self._buttons_frame, 'submit', (0, 1), self._submit_cmd)
        self._submit_btn.draw(sticky=tk.EW)

        self._table_menu_options = [f'table {i + 1}' for i in range(num_of_tables)]
        self._table_menu = ttk.Combobox(self._buttons_frame, values=self._table_menu_options, state='readonly')
        self._table_menu.current(0)
        self._table_menu.grid(row=0, column=2, sticky=tk.NSEW)

    def focus_set(self):
        self._my_window.focus_set()

    def _close_cmd(self, *_):
        self._menu.auto_insert_closed()
        self._my_window.destroy()

    def _submit_cmd(self, *_):
        self._menu.auto_insert([item.value for item in self._start_ip],
                               [item.value for item in self._end_ip],
                               self._index)
        self._close_cmd()

    @property
    def _index(self):
        return self._table_menu_options.index(self._table_menu.get())


class LogWin:
    def __init__(self, master, menu):
        self._master = master
        self._menu = menu

        self._my_window = tk.Toplevel(master)
        self._my_window.geometry('750x250')
        self._my_window.resizable(True, True)
        self._my_window.title('Log')
        self._my_window.protocol('WM_DELETE_WINDOW', self._close_cmd)

        self._main_menu = tk.Menu(self._my_window, tearoff=False)
        self._filter_menu = tk.Menu(self._main_menu, tearoff=False)
        self._main_menu.add_cascade(label='filter', menu=self._filter_menu)
        self._filters_value = {}
        self._set_filters()

        self._text = tk.Text(self._my_window, height=6, width=40, font=('Courier New', 8))
        self._text.tag_config('rtl', justify=tk.RIGHT)
        self._vsb = tk.Scrollbar(self._my_window, orient='vertical', command=self._text.yview)
        self._text.configure(yscrollcommand=self._vsb.set)
        self._vsb.pack(side='right', fill='y')
        self._text.pack(side='left', fill='both', expand=True)
        self._check_btn_v = tk.IntVar()
        self._check_button = tk.Checkbutton(self._my_window, text='auto scroll', variable=self._check_btn_v)
        self._check_button.select()
        self._check_button.pack(side=tk.TOP)

        self._last_value = []

        self._my_window.after(0, self._update)
        self._my_window.config(menu=self._main_menu)

    @property
    def checked_filters(self):
        return {key for key in self._filters_value if self._filters_value[key].get()}

    def focus_set(self):
        self._my_window.focus_set()

    def _close_cmd(self, *_):
        self._menu.log_win_closed()
        self._my_window.destroy()

    def _update(self):
        if len(log.hostnames) != len(self._filters_value):
            self._set_filters()
        new_value = self._filter(log.get_string_rtl())
        if new_value != self._last_value:
            current_pos = self._text.yview()[0]
            self._text.delete('1.0', tk.END)
            for line in new_value:
                self._text.insert(tk.END, line, 'rtl')
            self._text.yview_moveto(current_pos)
            if self._check_btn_v.get():
                self._text.see(tk.END)
            self._last_value = new_value
        self._my_window.after(settings.ping_sleep_timer, self._update)

    def _set_filters(self):
        for index, hostname in enumerate(log.hostnames):
            hostname = hebrew_reshaper(hostname).strip()
            if hostname not in self._filters_value:
                value = tk.IntVar()
                value.set(1)
                self._filters_value[hostname] = value
                self._filter_menu.add_checkbutton(label=hostname, variable=value)

    def _filter(self, content):
        filtered_content = []
        lines = content.split('\n')
        checked_filters = self.checked_filters
        for line in lines:
            for hostname in checked_filters:
                if hostname in line:
                    filtered_content.append(line+'\n')
                    break
        return filtered_content


class AddDataFrame:
    def __init__(self, master: tk.Misc, pos, tables: List[PingTable]):
        self._master = master
        self._pos = pos
        self._tables = tables
        self._frame = tk.Frame(self._master)
        self._name_input = Inputbox(self._frame, 'Host Name', (0, 0))
        self._ip_input = Inputbox(self._frame, 'Ip Address', (0, 1))
        self._submit_button = Button(self._frame, 'Submit', (0, 2), self._submit_func)

        self._table_menu_options = [f'table {i + 1}' for i in range(len(self._tables))]
        self._table_menu = ttk.Combobox(self._frame, values=self._table_menu_options, state='readonly')
        self._table_menu.current(0)

        for i in range(4):
            self._frame.grid_columnconfigure(i, weight=1)
        row, column = self._pos
        self._frame.grid(row=row, column=column, sticky=tk.EW, columnspan=settings.num_of_tables)
        self._name_input.draw(sticky=tk.EW)
        self._ip_input.draw(sticky=tk.EW)
        self._submit_button.draw(sticky=tk.EW)
        self._table_menu.grid(row=0, column=3, sticky=tk.NSEW)

    def _submit_func(self):
        if self._valid_data:
            self._tables[self._index].add((self._name_input.value, self._ip_input.value))
            self._master.focus_set()
            self._name_input.reset_text()
            self._ip_input.reset_text()

    @property
    def _valid_data(self):
        if self._name_input.changed and self._name_input.value != '':
            if len(self._name_input.value) > MAX_SUBJECT_LENGTH - 2:
                msgbox.showerror('Error!', f'Host Name is Longer then {MAX_SUBJECT_LENGTH - 2} Chars!')
                return False
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

    @property
    def _index(self):
        return self._table_menu_options.index(self._table_menu.get())

    def set_num_of_table(self):
        self._table_menu_options = [f'table {i + 1}' for i in range(len(self._tables))]
        self._table_menu.config(values=self._table_menu_options)
        self._table_menu.current(0)


class Menu:
    def __init__(self, master, tables: List[PingTable], tables_pd: tk.PanedWindow, add_data_frame: AddDataFrame):
        self._master = master
        self._tables = tables
        self._tables_pd = tables_pd
        self._add_data_frame = add_data_frame

        self._file_name = ''
        self._settings_win: Optional[SettingsWindow] = None
        self._auto_insert_win: Optional[AutoInsertWin] = None
        self._log_win: Optional[LogWin] = None

        self._main_menu = tk.Menu(master, tearoff=False)
        self._file_menu = tk.Menu(self._main_menu, tearoff=False)
        self._log_menu = tk.Menu(self._main_menu, tearoff=False)

        self._main_menu.add_cascade(label='file', menu=self._file_menu)

        self._file_menu.add_command(label='open', command=self.open_file_cmd)
        self._file_menu.add_command(label='new', command=self.new_file_cmd)
        self._file_menu.add_separator()
        self._file_menu.add_command(label='save', command=self.save_file_cmd)
        self._file_menu.entryconfig('save', state='normal' if self._file_name else 'disable')
        self._file_menu.add_command(label='save as', command=self.save_as_file_cmd)

        self._main_menu.add_command(label='settings', command=self._open_settings_cmd)

        self._main_menu.add_command(label='auto insert', command=self._auto_insert_cmd)

        self._main_menu.add_cascade(label='log', menu=self._log_menu)
        self._log_menu.add_command(label='open', command=self._open_log_cmd)

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
                    content = [item.split('->', 1) for item in content]
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
                    self._set_title()
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
            self._set_title()
            self._file_menu.entryconfig('save', state='normal')
            return True
        return False

    def _set_title(self):
        self._master.title(os.path.basename(self._file_name))

    def settings_closed(self):
        self._settings_win = None

    def _open_settings_cmd(self):
        if not self._settings_win:
            self._settings_win = SettingsWindow(self._master, self)
        self._settings_win.focus_set()

    def auto_insert_closed(self):
        self._auto_insert_win = None

    def _auto_insert_cmd(self):
        if not self._auto_insert_win:
            self._auto_insert_win = AutoInsertWin(self._master, self, len(self._tables))
        self._auto_insert_win.focus_set()

    def auto_insert(self, start_ip, end_ip, table_index):
        for a in range(start_ip[0], end_ip[0] + 1):
            for b in range(start_ip[1], end_ip[1] + 1):
                for c in range(start_ip[2], end_ip[2] + 1):
                    for d in range(start_ip[3], end_ip[3] + 1):
                        self._tables[table_index].add(('auto', f'{a}.{b}.{c}.{d}'))

    def log_win_closed(self):
        self._log_win = None

    def _open_log_cmd(self):
        if not self._log_win:
            self._log_win = LogWin(self._master, self)
        self._log_win.focus_set()

    def set_num_of_table(self, num_of_tables):
        if num_of_tables != len(self._tables):
            while len(self._tables) > num_of_tables:
                table = self._tables[-1]
                table.move_table_cmd()
                table.delete()
                self._tables.pop()
            while len(self._tables) < num_of_tables:
                self._tables.append(PingTable(self._tables_pd, (1, len(self._tables)), self._tables, len(self._tables)))
            for table in self._tables:
                self._master.after(0, table.set_size)
        self._add_data_frame.set_num_of_table()


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


def pinger_thread(table_line: PingTableLine, identifier):
    ip = table_line.ip_address
    ping_socket = PingSocket(ip, identifier)
    while settings.running and table_line.is_alive:
        start_time = datetime.datetime.now()
        if table_line.pause:
            time.sleep(settings.ping_sleep_timer / 1000)
            table_line.update_line(Color.GRAY)
            continue
        ping_socket.ip = table_line.ip_address
        ping_socket.send(settings.ping_buffer_size, settings.ping_ttl, settings.ping_timeout)
        answer, rtt = ping_socket.receive()
        if rtt:
            color = Color.YELLOW if rtt < settings.dock_time else Color.GREEN
        else:
            color = Color.RED
        time_str = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        table_line.add_data(f'{time_str} -> {answer}', color)
        table_line.update_line(color)
        to_sleep = max(settings.ping_sleep_timer / 1000 - (datetime.datetime.now() - start_time).total_seconds(), 0)
        time.sleep(to_sleep)


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
