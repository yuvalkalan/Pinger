# import time, pyautogui
# import PySimpleGUI as sg
# import multiprocessing
#
#
# def KeepUI():
#     sg.theme('Dark')
#     layout = [
#         [sg.Text(
#             'Keep-Me-Up is now running.\nYou can keep it minised, and it will continue running.\nClose it to disable it.')]
#     ]
#     window = sg.Window('Keep-Me-Up', layout)
#
#     p2 = multiprocessing.Process(target=dontsleep)
#     p2.start()
#
#     while True:
#         event, values = window.read()
#         if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
#             if p2.is_alive():
#                 p2.terminate()
#             break
#
#
# def dontsleep():
#     while True:
#         pyautogui.press('volumedown')
#         time.sleep(1)
#         pyautogui.press('volumeup')
#         time.sleep(300)
#
#
# if __name__ == '__main__':
#     p1 = multiprocessing.Process(target=KeepUI)
#     p1.start()

from tkinter import *
from tkinter.ttk import *


def main():
    for i in range(9, 10):
        print(i)
    root = Tk()
    tree = Treeview(root, selectmode="extended", columns=("A", "B"))
    tree.pack(expand=YES, fill=BOTH)
    tree.heading("#0", text="C/C++ compiler")
    tree.column("#0", minwidth=0, width=100, stretch=NO)
    tree.heading("A", text="A")
    tree.column("A", minwidth=0, width=200, stretch=NO)
    tree.heading("B", text="B")
    tree.column("B", minwidth=0, width=300)
    btn = Button(root, text='check', command=lambda: print(tree.column('A')))
    btn.pack()
    root.mainloop()


if __name__ == '__main__':
    main()