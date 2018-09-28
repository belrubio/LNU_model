import Tkinter as tk
from Tkinter import *
import ttk
 
# Root class to create the interface and define the controller function to switch frames
class RootApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(NoteBook)
 
# controller function
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
 
# sub-root to contain the Notebook frame and a controller function to switch the tabs within the notebook
class NoteBook(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.notebook = ttk.Notebook()
        self.tab1 = Tab1(self.notebook)
        self.tab2 = Tab2(self.notebook)
        self.tab3 = Tab3(self.notebook)
        self.notebook.add(self.tab1, text="Tab1")
        self.notebook.add(self.tab2, text="Tab2")
        self.notebook.add(self.tab3, text="Tab3")
        #self.tab1.grid(column=2, row=2)
        self.notebook.pack()
 
# controller function
    def switch_tab1(self, frame_class):
        new_frame = frame_class(self.notebook)
        self.tab1.destroy()
        self.tab1 = new_frame
         
# Notebook - Tab 1
class Tab1(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self._frame = None
        # layout all of the main containers
        #self.grid_rowconfigure(1, weight=1)
        #self.grid_columnconfigure(3, weight=1)
        ctr_mid = Frame(self, bg='red', width=250, height=300, padx=3, pady=3)
        ctr_left = Frame(self, bg='blue', width=100, height=190, padx=3, pady=3)
        ctr_bottom = Frame(self, bg='yellow', width=250, height=190, padx=3, pady=3)
        ctr_right = Frame(self, bg='green', width=100, height=190, padx=3, pady=3)

        #ctr_bottom.grid(row=0, column=1, sticky="sew")

        self.label = Label(ctr_mid, text="this is a test - one")
        #self.label.grid(row=0, sticky=S)
        e1 = Entry(ctr_mid, background="orange")

        ctr_mid.pack(side = TOP)
        ctr_left.pack(side = LEFT)
        ctr_bottom.pack(side = BOTTOM)
        ctr_right.pack(side = RIGHT)
        self.label.pack()
        e1.pack()

        #self.switch_frame(Tab1_Frame1)
 
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
 
# # first frame for Tab1
# class Tab1_Frame1(Frame):
#     def __init__(self, master):
#         Frame.__init__(self, master)
#         self.label = Label(self, text="this is a test - one")
#         #self.label.grid(row=0, sticky=S)
#         e1 = Entry(self, background="orange")
#         # self.e1.grid(row=1, sticky=W)

#         # top_frame.grid(column=0, row=0, columnspan=3, rowspan=2)
#         # center.grid(row=1, sticky="nsew")
#         # btm_frame.grid(row=3, sticky="ew")
#         # btm_frame2.grid(row=4, sticky="ew")

#         # # create the widgets for the top frame
#         #model_label = Label(top_frame, text='Model Dimensions')
#         #width_label = Label(top_frame, text='Train')
#         #length_label = Label(top_frame, text='Lesion')
#         # entry_W = Entry(top_frame, background="pink")
#         # entry_L = Entry(top_frame, background="orange")

#         # # layout the widgets in the top frame
#         # model_label.grid(row=0, columnspan=3)
#         # width_label.grid(row=1, column=0)
#         # length_label.grid(row=1, column=2)
#         # entry_W.grid(row=1, column=1)
#         # entry_L.grid(row=1, column=3)

#         # # create the center widgets
#         # center.grid_rowconfigure(0, weight=1)
#         # center.grid_columnconfigure(1, weight=1)

#         # ctr_left = Frame(center, bg='blue', width=100, height=190)
#         # ctr_mid = Frame(center, bg='yellow', width=250, height=190, padx=3, pady=3)
#         # ctr_right = Frame(center, bg='green', width=100, height=190, padx=3, pady=3)

#         # ctr_left.grid(row=0, column=0, sticky="ns")
#         # ctr_mid.grid(row=0, column=1, sticky="nsew")
#         # ctr_right.grid(row=0, column=2, sticky="ns")

#         # button object with command to replace the frame
#         self.button = Button(self, text="Change it!", command=lambda: master.switch_frame(Tab1_Frame2))
#         self.button.grid(row=2, sticky=S)
#         self.label.pack(side = RIGHT)
#         self.button.pack(side = LEFT)
#         e1.pack(side = BOTTOM)
 
# # second frame for Tab1
# class Tab1_Frame2(Frame):
#     def __init__(self, master):
#         Frame.__init__(self, master)
#         self.label = Label(self, text="it has been changed!")
#         # and another button to change it back to the previous frame
#         self.button = Button(self, text="Change it back!", command=lambda: master.switch_frame(Tab1_Frame1))
#         self.label.pack()
#         self.button.pack()
 
# Notebook - Tab 2
class Tab2(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, text="this is a test - two")
        self.label.pack()
 
# Notebook - Tab 3
class Tab3(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, text="this is a test - three")
        self.label.pack()
 
if __name__ == "__main__":
    Root = RootApp()
    Root.geometry("640x480")
    Root.title("Frame test")
    Root.mainloop()