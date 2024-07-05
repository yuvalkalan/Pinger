import tkinter as tk


class window2:
    def __init__(self, master1: tk.Tk):
        self.panel2 = tk.Frame(master1)
        self.panel2.grid()
        self.button2 = tk.Button(self.panel2, text = "Quit", command = self.panel2.quit)
        self.button2.grid()
        vcmd = (self.panel2.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.text1 = tk.Entry(self.panel2, validate = 'key', validatecommand=vcmd)
        self.text1.grid()
        self.text1.focus()

    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        print('action:',action,
              'index:',index,
              'value_if_allowed:',value_if_allowed,
              'prior_value:',prior_value,
              'text:',text,
              'validation_type:',validation_type,
              'trigger_type:',trigger_type,
              'widget_name:', widget_name)

        if value_if_allowed:
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return True

root1 = tk.Tk()
window2(root1)
root1.mainloop()