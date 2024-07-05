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
    # root.geometry(SCREEN_SIZE)
    root.title(SCREEN_TITLE)
    return root


def main():
    root = init_root()
    settings.add_root(root)
    tables = []
    sys.argv.append('hi.pngr')
    for i in range(settings.num_of_tables):
        tables.append(PingTable(root, (1, i), tables, i))
    main_menu = Menu(root, tables)
    if len(sys.argv) != 1:
        main_menu.open_file_cmd(sys.argv[1])
    # for i in range(255):
    #     tables[settings.table_adder].add(('hi', f'{i}.{i}.{i}.{i}'))
    AddDataFrame(root, (0, 0), tables)
    blank_frame = tk.Frame(root)
    blank_frame.grid(row=2, column=0)
    tk.Label(blank_frame, text='').pack()
    credit_label = tk.Label(root, text='Pinger++ by Yuval Kalanthroff', bd=1, relief=tk.SUNKEN)
    credit_label.place(relx=0.5, rely=1.0, anchor='s', relwidth=1.0)
    root.protocol('WM_DELETE_WINDOW', lambda: do_quit(root, tables, main_menu))
    tk.mainloop()


if __name__ == '__main__':
    main()
