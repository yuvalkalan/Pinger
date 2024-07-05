from tkinter import *

root = Tk()

m_frame = Frame(root)
m_frame.pack(fill=BOTH, expand=1)
my_canvas = Canvas(m_frame)
my_canvas.pack(side=LEFT)
scollbar = Scrollbar(m_frame, orient=VERTICAL, command=my_canvas.yview)
scollbar.pack(side=RIGHT, fill=Y)
my_canvas.config(yscrollcommand=scollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.config(scrollregion=my_canvas.bbox('all')))
sub_frame = Frame(my_canvas)
my_canvas.create_window((0, 0), window=sub_frame, anchor='nw')

for _ in range(100):
    Label(sub_frame, text='hi!').pack()
root.mainloop()