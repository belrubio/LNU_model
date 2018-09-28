import Tkinter as tk
from Tkinter import *
import ttk
from Model import *
 
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
        self.tab4 = Tab4(self.notebook)
        self.notebook.add(self.tab1, text="Training")
        self.notebook.add(self.tab2, text="Stroke")
        self.notebook.add(self.tab3, text="Recovery")
        self.notebook.add(self.tab4, text="Follow-up")
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
        top_frame = Frame(self, bg='gray85', width=30, height=10, pady=3)
        center = Frame(self, bg='gray85', width=1350, height=10, padx=3, pady=3)
        btm_frame = Frame(self, bg='gray99', width=1350, height=425, pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=3, sticky="ew")

                # create the top frame widgets
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        ctr_left = Frame(top_frame, bg='azure2', width=300, height=270)
        ctr_mid = Frame(top_frame, bg='mint cream', width=300, height=300, padx=3, pady=3)
        ctr_right = Frame(top_frame, bg='LightCyan2', width=730, height=300, padx=3, pady=3)

        ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_right.grid(row=0, column=2, sticky="ns")

        # create the widgets for the top frame 
        model_label = Label(ctr_mid, text='Free Parameters', font=("Helvetica", 16), anchor=W, justify=LEFT, bg='mint cream')
        label1 = Label(ctr_mid, text='UD Learning Rate:', bg='mint cream', anchor=W)
        label2 = Label(ctr_mid, text='EB Learning Rate:', bg='mint cream')
        label3 = Label(ctr_mid, text='RB Learning Rate:', bg='mint cream')
        label4 = Label(ctr_mid, text='Exploration Level:', bg='mint cream')
        label5 = Label(ctr_mid, text='Right Dominance:', bg='mint cream')
        #label6 = Label(ctr_mid, text='Cost Ratio (C/I):', bg='mint cream')
        label6 = Label(ctr_mid, text='Number of Trials:', bg='mint cream')
        
        entry1 = Entry(ctr_mid, background="LightBlue3", width=6)
        entry2 = Entry(ctr_mid, background="LightBlue3", width=6)
        entry3 = Entry(ctr_mid, background="LightBlue3", width=6)
        entry4 = Entry(ctr_mid, background="LightBlue3", width=6)
        entry5 = Entry(ctr_mid, background="LightBlue3", width=6)
        #entry6 = Entry(ctr_mid, background="LightBlue3", width=6)
        entry6 = Entry(ctr_mid, background="LightBlue2", width=6)
        run_button = Button(ctr_mid, text="RUN SIMULATION", bg="red", command=self.switch_frame)
        

        # layout the widgets in the top frame
        model_label.grid(row=0, column=3, columnspan=30)
        label1.grid(row=1, column=1)
        label2.grid(row=2, column=1)
        label3.grid(row=3, column=1)
        label4.grid(row=4, column=1)
        label5.grid(row=5, column=1)
        #label6.grid(row=6, column=1)
        label6.grid(row=6, column=1)
        entry1.grid(row=1, column=3)
        entry2.grid(row=2, column=3)
        entry3.grid(row=3, column=3)
        entry4.grid(row=4, column=3)
        entry5.grid(row=5, column=3)
        #entry6.grid(row=6, column=3)
        entry6.grid(row=6, column=3)
        #run_button.pack(side="bottom")
        run_button.grid(row=10, column=3)

        # layout top Left
        #photo = PhotoImage(file="test.gif", width=300)
        #w = Label(ctr_left, image=photo)
        #w.photo = photo
        #w.pack()

        #self.switch_frame(Tab1_Frame1)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
 
 
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

# Notebook - Tab 4
class Tab4(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, text="this is a test - three")
        self.label.pack()
 
if __name__ == "__main__":
    Root = RootApp()
    Root.resizable(width=FALSE, height=FALSE)
    Root.geometry("1380x1050")
    Root.title("Recovery Model Interface")
    Root.mainloop()