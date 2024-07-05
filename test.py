import time
import tkinter as tk
from tkinter import ttk


class Example(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.text = tk.Text(self, height=6, width=40)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.check_btn_v = tk.IntVar()
        self.check_button = tk.Checkbutton(self, text="auto scroll", variable=self.check_btn_v)
        self.check_button.pack(side=tk.TOP)

        self.add_timestamp()

    def add_timestamp(self):
        self.text.insert("end", time.ctime() + "\n")
        if self.check_btn_v.get():
            self.text.see("end")
        self.after(1000, self.add_timestamp)


if __name__ == "__main__":
    root = tk.Tk()
    frame = Example(root)
    frame.pack(fill="both", expand=True)
    root.mainloop()
