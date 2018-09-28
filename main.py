import matplotlib
matplotlib.use("TkAgg")
import tkinter as tk
import ttk
import numpy as np
from tabGUI import *


# Root class to create the interface and define the controller function to
# switch frames
class RootApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(NoteBook)
        self.style = None

# controller function
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


# sub-root to contain the Notebook frame and a controller function to switch
# the tabs within the notebook
class NoteBook(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.notebook = ttk.Notebook()
        self.tab1 = tabGUI(self.notebook, 'Training')
        self.tab2 = tabGUI(self.notebook, 'Stroke')
        self.tab3 = tabGUI(self.notebook, 'Rehab')
        self.tab4 = tabGUI(self.notebook, 'Followup')
        self.notebook.add(self.tab1, text="Training")
        self.notebook.add(self.tab2, text="Stroke")
        self.notebook.add(self.tab3, text="Recovery")
        self.notebook.add(self.tab4, text="Follow-up")
        self.notebook.pack()


if __name__ == "__main__":
    Root = RootApp()
    Root.resizable(width=False, height=False)
    Root.geometry("1360x1060")
    Root.title("Recovery Model Interface")
    Root.mainloop()
