"""
pinger++ v19.1 by Yuval Kalanthroff
he + rtl version
new version - bug fix
07.07.24
may the white rotem be with you
"""

from classes import *
import sys


def do_quit(root, tables, main_menu):
    if ask_for_save(tables, main_menu):
        settings.running = False
        for table in tables:
            table.join()
        root.destroy()


def init_root():
    root = tk.Tk()
    stl = ttk.Style()
    theme = stl.theme_use()
    stl.theme_create('wrapper', parent=theme)
    stl.theme_use('wrapper')
    stl.map('Treeview', background=[('selected', SELECTED_COLOR)])
    root.geometry(SCREEN_SIZE)
    root.title(DEF_SCREEN_TITLE)
    return root


def main():
    root = init_root()
    settings.add_root(root)
    tables = []
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    tables_pd = tk.PanedWindow(root, bg='black')
    tables_pd.grid(row=1, column=0, sticky=tk.NSEW)
    for i in range(settings.num_of_tables):
        tables.append(PingTable(tables_pd, (1, i), tables, i))
    add_data_frame = AddDataFrame(root, (0, 0), tables)
    main_menu = Menu(root, tables, tables_pd, add_data_frame)
    if len(sys.argv) != 1:
        main_menu.open_file_cmd(sys.argv[1])
    blank_frame = tk.Frame(root)
    blank_frame.grid(row=2, column=0)
    tk.Label(blank_frame, text='').pack()
    current_time = datetime.datetime.now().strftime('%d.%m %H:%M')
    credit_label = tk.Label(root, text=f"Pinger++ by Yuval Kalanthroff, Opened at {current_time}",
                            bd=1, relief=tk.SUNKEN)
    credit_label.place(relx=0.5, rely=1.0, anchor='s', relwidth=1.0)
    root.protocol('WM_DELETE_WINDOW', lambda: do_quit(root, tables, main_menu))
    tk.mainloop()
    log.add('מערכת', 'נסגר בהצלחה')
    log.update()


if __name__ == '__main__':
    main()
