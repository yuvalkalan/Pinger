import subprocess
import threading
import time
from typing import *
import tkinter as tk
from tkinter import filedialog as fd, messagebox as msgbox


BLACK = '#000000'
RED = '#FF0000'
GREEN = '#00FF00'
BLUE = '#0000FF'
WHITE = '#FFFFFF'
YELLOW = '#FFFF00'

DEF_TEXT_SIZE = 20

DEF_TEXT_COLOR = None
DEF_TEXT_BG_COLOR = None
SCREEN_SIZE = '1000x500'
SCREEN_TITLE = 'BetterPinger'

UP = tk.N
DOWN = tk.S
RIGHT = tk.E
LEFT = tk.W

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
        self._font = ("Arial", self._size)
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


class Button(Text):
    def __init__(self, master, text, pos, func, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR, size=DEF_TEXT_SIZE):
        super(Button, self).__init__(master, text, pos, color, bg_color, size)
        self._func = func
        self._widget = tk.Button(master, text=text, fg=color, bg=bg_color, command=func, font=self._font)


class InputBox(Text):
    def __init__(self, master, text, pos, color=BLACK, bg_color=DEF_TEXT_BG_COLOR, size=DEF_TEXT_SIZE):
        super(InputBox, self).__init__(master, text, pos, color, bg_color, size)
        self._widget = tk.Entry(master, fg='gray', bg=bg_color, font=self._font)
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
        self._widget.config(foreground='gray')
        self._changed = False

    @property
    def value(self):
        return self._widget.get()

    @property
    def changed(self):
        return self._changed


class Table:
    def __init__(self, master: tk.Misc, titles, pos):
        self._master = master
        self._frame = tk.Frame(self._master, bg=BLACK)
        self._pos = pos
        self._titles = []
        for index, title in enumerate(titles):
            self._titles.append(Text(self._frame, title, (0, index), size=2*DEF_TEXT_SIZE))
            self._frame.grid_columnconfigure(index, weight=1)
        self._values: List[List[Text]] = [[] for _ in range(len(self._titles))]

    def add(self, row):
        for index, value in enumerate(row):
            grid_pos = (len(self._values[index]) + 1, index)
            self._values[index].append(Text(self._frame, value, grid_pos, bg_color=WHITE))
        self._update_draw()

    def draw(self):
        row, column = self._pos
        self._frame.grid(row=row, column=column, sticky=tk.EW)
        for title in self._titles:
            title.draw(sticky=tk.EW, padx=2, pady=2)
        for lst in self._values:
            for value in lst:
                value.draw(sticky=tk.EW, padx=2, pady=2)

    def _update_draw(self):
        for lst in self._values:
            lst[-1].draw(sticky=tk.EW, padx=2, pady=2)

    @property
    def items(self):
        hosts, ips = self._values
        return [(hosts[i].text, ips[i].text) for i in range(len(hosts))]


def add_pinger(name_obj: Text, ip_obj: Text, settings: Settings):
    ip = ip_obj.text
    while settings.running:
        output = subprocess.getoutput(f"ping {ip} -n 1")
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
        name_obj.bg_color = color
        ip_obj.bg_color = color
        time.sleep(1)


class PingTable(Table):
    def __init__(self, master: tk.Misc, pos, settings):
        super(PingTable, self).__init__(master, ('Host Name', 'Ip Address'), pos)
        self._master.after(100, self._check_pingers)
        self._ping_list: List[threading.Thread] = []
        self._settings = settings

    def add(self, row):
        super(PingTable, self).add(row)
        name, ip = [lst[-1] for lst in self._values]
        thread = threading.Thread(target=add_pinger, args=[name, ip, self._settings])
        self._ping_list.append(thread)
        thread.start()

    def join(self):
        for thread in self._ping_list:
            thread.join()

    def reset(self):
        self._settings.running = False
        self.join()
        self._ping_list = []
        self._settings.running = True
        for lst in self._values:
            for item in lst:
                item.destroy()
        self._values = [[] for _ in range(len(self._titles))]

    def _check_pingers(self):
        for lst in self._values:
            for item in lst:
                if item.bg_color_changed:
                    item.change_background()
        self._master.after(100, self._check_pingers)


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
        self._file_name = fd.askopenfilename(title='Open File', filetypes=FILE_TYPES, defaultextension=".pngr")
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
        filename = fd.asksaveasfilename(title='Save File', filetypes=FILE_TYPES, defaultextension=".pngr")
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


def main():
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(SCREEN_TITLE)
    root.grid_columnconfigure(0, weight=1)
    settings = Settings()
    table = PingTable(root, (1, 0), settings)
    # for i in range(100):
    #     table.add((f'item{i}', f'{i}.{i}.{i}.{i}'))
    table.draw()
    menu = Menu(root, table)
    add_data_frame = AddDataFrame(root, (0, 0), table)
    add_data_frame.draw()
    credit_label = tk.Label(root, text='Pinger++ by Yuval Kalanthroff', bg='gray')
    credit_label.place(relx=0.5, rely=1.0, anchor='s', relwidth=1.0)
    tk.mainloop()
    settings.running = False
    table.join()


if __name__ == '__main__':
    main()
