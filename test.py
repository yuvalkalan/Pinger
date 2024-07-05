import tkinter as tk

root = tk.Tk()
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frame = tk.Frame(root, bg='black')
frame.grid(row=0, column=0, sticky=tk.NSEW)
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)


pd1 = tk.PanedWindow(frame, orient=tk.HORIZONTAL, bg='black')
pd1.grid(row=0, column=0, sticky=tk.NSEW)

l_frame = tk.Frame(pd1)
pd1.add(l_frame)

left_label = tk.Label(l_frame, text="left")
left_label.grid(row=0, column=0, sticky=tk.EW)

for i in range(10):
    t_frame = tk.Frame(pd1)
    pd1.add(t_frame)

    top_label = tk.Label(t_frame, text="left")
    top_label.grid(row=0, column=0, sticky=tk.EW)


tk.mainloop()
