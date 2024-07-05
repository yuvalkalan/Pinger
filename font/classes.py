from .constants import *
from log import *
import tkinter as tk


class Text:
    def __init__(self, master: tk.Misc, text: str, pos, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR,
                 size=Default.TEXT_SIZE):
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
    def __init__(self, master: tk.Misc, text: str, pos, func, color=DEF_TEXT_COLOR, bg_color=DEF_TEXT_BG_COLOR,
                 size=Default.TEXT_SIZE):
        super(Button, self).__init__(master, text, pos, color, bg_color, size)
        self._func = func
        self._widget = tk.Button(master, text=text, fg=color, bg=bg_color, command=func, font=self._font)


class Inputbox(Text):
    def __init__(self, master: tk.Misc, text: str, pos, color=Color.BLACK, bg_color=DEF_TEXT_BG_COLOR,
                 size=Default.TEXT_SIZE):
        super(Inputbox, self).__init__(master, text, pos, color, bg_color, size)
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
    def __init__(self, master: tk.PanedWindow, titles, pos):
        row, column = pos
        # make table resizable
        master.grid_rowconfigure(row, weight=1)
        master.grid_columnconfigure(column, weight=1)
        self._master = master
        self._frame = tk.Frame(master)
        master.add(self._frame, stretch='always')
        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=1)
        # create tree
        self._titles = titles
        self._tree = ttk.Treeview(self._frame, columns=titles, show='headings')
        for column in titles:
            self._tree.heading(column, text=column)
            self._tree.column(column, anchor='e', minwidth=1)
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
        self._master.after(0, self.set_size)

    def set_size(self):
        length = self._tree.winfo_width()
        for title in self._titles:
            self._tree.column(title, width=length // 4)

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
                    self._switch_pos(child, children[i - 1])
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

    def delete(self):
        self._master.remove(self._frame)


class FloatInputBox(Text):
    def __init__(self, master: tk.Misc, text: str, pos, from_, to, jump_by=1, color=Color.BLACK,
                 bg_color=DEF_TEXT_BG_COLOR, size=Default.TEXT_SIZE, on_change: Optional[Callable] = None):
        super(FloatInputBox, self).__init__(master, text, pos, color, bg_color, size)
        self._from = from_
        self._to = to
        validate_cmd = (master.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self._widget = tk.Spinbox(master, from_=from_, to=to, increment=jump_by, fg=color, font=self._font, bd=0,
                                  bg=bg_color, validate='key', validatecommand=validate_cmd, wrap=True,
                                  command=on_change)
        self._set_text(text)

    def validate(self, action, index, value_if_allowed: str, prior_value, text, validation_type, trigger_type,
                 widget_name):
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
            return max(min(float(v), self._to), self._from)
        return None

    def _set_text(self, text: str):
        self._widget.delete(0, tk.END)
        self._widget.insert(0, text)


class IntInputBox(FloatInputBox):
    def __init__(self, master: tk.Misc, text: str, pos, from_, to, jump_by=1, color=Color.BLACK,
                 bg_color=DEF_TEXT_BG_COLOR, size=Default.TEXT_SIZE, on_change=None):
        super(IntInputBox, self).__init__(master, text, pos, from_, to, jump_by, color, bg_color, size, on_change)

    def validate(self, action, index, value_if_allowed: str, prior_value, text, validation_type, trigger_type,
                 widget_name):
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
            return max(min(int(v), self._to), self._from)
        return None


class BoolInputBox(IntInputBox):
    def __init__(self, master: tk.Misc, text: str, pos, color=Color.BLACK, bg_color=DEF_TEXT_BG_COLOR,
                 size=Default.TEXT_SIZE, on_change=None):
        super(IntInputBox, self).__init__(master, text, pos, None, None, 1, color, bg_color, size, on_change)
        self._values = ['True', 'False']
        self._widget.config(values=self._values)
        self._set_text(text)

    def validate(self, action, index, value_if_allowed: str, prior_value, text, validation_type, trigger_type,
                 widget_name):
        if value_if_allowed:
            if value_if_allowed not in ['True', 'False']:
                return False
        return True

    @property
    def value(self):
        v = self._widget.get()
        if v:
            return 1 if v == 'True' else 0
        return None
