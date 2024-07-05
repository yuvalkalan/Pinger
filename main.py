import subprocess
import threading
import time
from typing import List, Optional, Tuple
import tkinter as tk
from tkinter import filedialog as fd, messagebox as msgbox

COLOR = str
POSITION = Tuple[int, int]

BLACK: COLOR = '#000000'
RED: COLOR = '#FF0000'
GREEN: COLOR = '#00FF00'
BLUE: COLOR = '#0000FF'
WHITE: COLOR = '#FFFFFF'
YELLOW: COLOR = '#FFFF00'
GRAY: COLOR = '#808080'

DEF_TEXT_SIZE = 20

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
              'destination port unreachable']
FILE_TYPES = (('Pinger Files (*.pngr)', '*.pngr'), ('All Files (*.*)', '*.*'))

DOCK_PARAM = 100


class Settings:
    def __init__(self):
        self._running = True

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, running):
        self._running = running


class Text:
    def __init__(self, master, text, pos, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR, size=DEF_TEXT_SIZE):
        self._text = text
        self._color = color
        self._size = size
        self._pos = pos
        self._bg_color = bg_color
        self._bg_color_changed = False
        self._font = ('Arial', self._size)
        self._widget = tk.Entry(master, fg=color, readonlybackground=bg_color, font=self._font, bd=0)
        self._widget.insert(0, text)
        self._widget.config(state='readonly')
        self._is_dead = False

    def draw(self, **kwargs):
        row, column = self._pos
        self._widget.grid(row=row, column=column, **kwargs)

    def pack(self, pos=None):
        if pos:
            self._widget.pack(pos)
        else:
            self._widget.pack()

    @property
    def text(self):
        return self._text

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

    def change_background(self):
        self._widget.config(readonlybackground=self._bg_color)

    def destroy(self):
        self._widget.destroy()

    def bind(self, event, handler):
        self._widget.bind(event, handler)


class Button(Text):
    def __init__(self, master, text, pos, func, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR, size=DEF_TEXT_SIZE):
        super(Button, self).__init__(master, text, pos, color, bg_color, size)
        self._func = func
        self._widget = tk.Button(master, text=text, fg=color, bg=bg_color, command=func, font=self._font)


class InputBox(Text):
    def __init__(self, master, text, pos, color=BLACK, bg_color=DEF_TEXT_BG_COLOR, size=DEF_TEXT_SIZE):
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


class TableLine:
    def __init__(self, table_frame, params: List[str], row_index):
        self._table_frame = table_frame
        self._params: List[Text] = []
        for i, p in enumerate(params):
            self._params.append(Text(table_frame, p, (row_index, i), bg_color=WHITE))

    def draw(self, **kwargs):
        for param in self._params:
            param.draw(**kwargs)

    def destroy(self):
        for param in self._params:
            param.destroy()

    @property
    def bg_color(self):
        return self._params[0].bg_color

    @bg_color.setter
    def bg_color(self, color):
        for param in self._params:
            param.bg_color = color

    def change_background(self):
        for param in self._params:
            param.change_background()


class Table:
    def __init__(self, master: tk.Misc, titles, pos):
        row, column = pos
        # make table resizable
        master.grid_rowconfigure(row, weight=1)
        # create resizable main frame
        self._main_frame = tk.Frame(master)
        self._main_frame.grid(row=row, column=column, sticky=tk.NSEW)
        self._main_frame.grid_columnconfigure(0, weight=1)
        self._main_frame.grid_rowconfigure(0, weight=1)
        # put canvas and scrollbar insize main frame
        self._canvas = tk.Canvas(self._main_frame)
        self._canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self._scrollbar = tk.Scrollbar(self._main_frame, orient=tk.VERTICAL, command=self._canvas.yview)
        self._scrollbar.grid(row=0, column=1, sticky=tk.NS)
        # config canvas
        self._canvas.config(yscrollcommand=self._scrollbar.set)
        self._frame = tk.Frame(self._canvas, bg=BLACK)
        self._canvas_frame = self._canvas.create_window((0, 0), window=self._frame, anchor='nw')
        self._canvas.bind('<Configure>', self._canvas_config)

        self._master = master
        self._titles = []
        for index, title in enumerate(titles):
            self._titles.append(Text(self._frame, title, (0, index), size=2 * DEF_TEXT_SIZE))
            self._frame.grid_columnconfigure(index, weight=1)
        self._lines: List[TableLine] = []

    def _canvas_config(self, e):
        self._canvas.itemconfig(self._canvas_frame, width=e.width)
        self._canvas.config(scrollregion=self._canvas.bbox('all'))

    def add(self, line):
        self._lines.append(TableLine(self._frame, line, len(self._lines)))
        self._update_draw()

    def draw(self):
        for title in self._titles:
            title.draw(sticky=tk.EW, padx=2, pady=2)
        for value in self._lines:
            value.draw(sticky=tk.EW, padx=2, pady=2)

    def _update_draw(self):
        self._lines[-1].draw(sticky=tk.EW, padx=2, pady=2)


class PingTableLine(TableLine):
    def __init__(self, master, table_frame, host_name, ip_address, row_index):
        super(PingTableLine, self).__init__(table_frame, [host_name, ip_address], row_index)
        self._my_window: Optional[tk.Toplevel] = None
        self._master = master
        self._data: List[Tuple[str, COLOR]] = []
        for line in self._params:
            line.bind('<Double-Button-1>', self.create_window)

    @property
    def host_name(self) -> Text:
        return self._params[0]

    @property
    def ip_address(self) -> Text:
        return self._params[1]

    @property
    def _have_window(self):
        return self._my_window is not None

    @property
    def _have_data(self):
        return self._data != []

    def add_data(self, data, color):
        if self._have_window:
            self._data.append((data, color))

    def create_window(self, _):
        if not self._have_window:
            self._my_window = tk.Toplevel(self._master, bg=GRAY)
            self._my_window.geometry('750x250')
            self._my_window.title(f'{self.host_name.text} ({self.ip_address.text})')
            self._my_window.protocol('WM_DELETE_WINDOW', self.close_window)
        self._my_window.focus_set()

    def close_window(self):
        self._my_window.destroy()
        self._my_window = None
        self._data = []

    def add_data_to_window(self):
        while self._have_data:
            data, color = self._data.pop(0)
            tk.Label(self._my_window, text=data, fg=color, bg=GRAY).pack(anchor=tk.W)


class PingTable(Table):
    def __init__(self, master: tk.Misc, pos, settings):
        super(PingTable, self).__init__(master, ('Host Name', 'Ip Address'), pos)
        self._master.after(100, self._check_pingers)
        self._ping_threads: List[threading.Thread] = []
        self._settings = settings

    def add(self, host_name_and_ip_address):
        name, ip = host_name_and_ip_address
        new_line = PingTableLine(self._master, self._frame, name, ip, len(self._lines) + 1)
        self._lines.append(new_line)
        self._update_draw()
        thread = threading.Thread(target=add_pinger, args=[new_line, self._settings])
        self._ping_threads.append(thread)
        thread.start()

    def join(self):
        for thread in self._ping_threads:
            thread.join()

    def reset(self):
        self._settings.running = False
        self.join()
        self._ping_threads = []
        self._settings.running = True
        for value in self._lines:
            value.destroy()
        self._lines: List[PingTableLine] = []

    def _check_pingers(self):
        for line in self._lines:
            line.change_background()
            line.add_data_to_window()
        self._master.after(100, self._check_pingers)

    @property
    def items(self):
        return [(line.host_name.text, line.ip_address.text) for line in self._lines]


class Menu:
    def __init__(self, master, table: PingTable):
        self._file_name = ''
        self._table = table
        self._main_menu = tk.Menu(master, tearoff=False)
        master.config(menu=self._main_menu)

        self._file_menu = tk.Menu(self._main_menu, tearoff=False)
        self._settings_menu = tk.Menu(self._main_menu, tearoff=False)

        self._main_menu.add_cascade(label='file', menu=self._file_menu)
        self._main_menu.add_cascade(label='settings', menu=self._settings_menu)

        self._file_menu.add_command(label='open', command=self._open_file_cmd)
        self._file_menu.add_separator()
        self._file_menu.add_command(label='save', command=self._save_file_cmd)
        self._file_menu.entryconfig('save', state='normal' if self._file_name else 'disable')
        self._file_menu.add_command(label='save as', command=self._save_as_file_cmd)

        self._settings_menu.add_command(label='text size', command=self._text_size_cmd)

    def _open_file_cmd(self):
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
                self._file_menu.entryconfig('save', state='normal')
            except Exception as e:
                msgbox.showerror('Error!', f'can\'t open file! {e}')

    def _save_file_cmd(self):
        if self._file_name:
            with open(self._file_name, 'w+') as my_file:
                for host, ip in self._table.items:
                    my_file.write(f'{host}->{ip}\n')

    def _save_as_file_cmd(self):
        filename = fd.asksaveasfilename(title='Save File', filetypes=FILE_TYPES, defaultextension='.pngr')
        if filename:
            with open(filename, 'w+') as my_file:
                for host, ip in self._table.items:
                    my_file.write(f'{host}->{ip}\n')
            self._file_menu.entryconfig('save', state='normal')

    def _text_size_cmd(self):
        pass


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


def add_pinger(table_line: PingTableLine, settings: Settings):
    ip = table_line.ip_address.text
    while settings.running:
        output = subprocess.getoutput(f'ping {ip} -n 1')
        output = output.split('\n')[2].lower()
        have_answer = [error_msg for error_msg in ERROR_MSGS if error_msg in output] == []
        if have_answer:
            params = output.split(': ')[1]
            p_bytes, p_time, p_ttl = params.split(' ')
            p_bytes = int(p_bytes.split('=')[1])
            p_time = int(p_time.split('=' if '=' in p_time else '<')[1].strip('ms'))
            p_ttl = int(p_ttl.split('=')[1])
            color = YELLOW if p_time < DOCK_PARAM else GREEN
        else:
            color = RED
        table_line.add_data(output, color)
        table_line.bg_color = color
        time.sleep(1)


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


def do_quit(root, settings, table):
    settings.running = False
    table.join()
    root.destroy()


def main():
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(SCREEN_TITLE)
    root.grid_columnconfigure(0, weight=1)
    settings = Settings()
    table = PingTable(root, (1, 0), settings)
    table.draw()
    for i in range(10):
        table.add(('hi', f'{i}.{i}.{i}.{i}'))
    menu = Menu(root, table)
    add_data_frame = AddDataFrame(root, (0, 0), table)
    add_data_frame.draw()
    credit_label = tk.Label(root, text='Pinger++ by Yuval Kalanthroff', bg=GRAY)
    credit_label.place(relx=0.5, rely=1.0, anchor='s', relwidth=1.0)
    root.protocol('WM_DELETE_WINDOW', lambda: do_quit(root, settings, table))
    tk.mainloop()


if __name__ == '__main__':
    main()
