#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com
# SPECS Lab. Institute of Bioengineering of Catalunya
#
# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#


import matplotlib
matplotlib.use("TkAgg")
import tkinter as tk
import ttk
import numpy as np
from tabGUI import *


# Color palettes
COLOR_TRAINING = ['Azure3', 'MintCream', 'Azure2', 'LightBlue3']
COLOR_STROKE = ['AntiqueWhite3', 'AntiqueWhite', 'AntiqueWhite2', "LightBlue3"]
COLOR_THERAPY = ['Honeydew3', 'Honeydew', 'Honeydew2', "mintcream"]
COLOR_FOLLOWUP = ['Snow3', 'whitesmoke', 'Snow2', "mintcream"]


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
        self.tab1 = tabGUI(self.notebook, 'Training', COLOR_TRAINING)
        self.tab2 = tabGUI(self.notebook, 'Stroke', COLOR_STROKE)
        self.tab3 = tabGUI(self.notebook, 'Rehab', COLOR_THERAPY)
        self.tab4 = tabGUI(self.notebook, 'Followup', COLOR_FOLLOWUP)
        self.notebook.add(self.tab1, text="Training")
        self.notebook.add(self.tab2, text="Stroke")
        self.notebook.add(self.tab3, text="Recovery")
        self.notebook.add(self.tab4, text="Follow-up")
        self.notebook.pack()


if __name__ == "__main__":
    Root = RootApp()
    Root.resizable(width=False, height=False)
    Root.geometry("1360x1060")
    Root.title("LNU Recovery Model Interface")
    Root.mainloop()
