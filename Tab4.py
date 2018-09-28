import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import tkinter as tk
import ttk
from SimulationsMain import *
import tkinter.filedialog
import tkinter.messagebox
import numpy as np

# Notebook - Tab 1
class Tab4(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self._frame = None

        #Vars for plotting
        self.data1 = []
        self.data2 = []
        self.data3 = []
        self.f = None

        # layout all of the main containers
        top_frame = tk.Frame(self, bg='gray97', width=1360, height=10, pady=3)
        center = tk.Frame(self, bg='gray97', width=1360, height=10, padx=3, pady=3)
        btm_frame = tk.Frame(self, bg='gray97', width=1360, height=180, pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="nsew")
        center.grid(row=1, sticky="ew")
        btm_frame.grid(row=2, sticky="nsew")
        #label_about = tk.Label(btm_frame, text='Info paper and references here', bg='mint cream')
        #label_about.grid(row=2, sticky="ew")

        # create the top frame widgets
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        ctr_left = tk.Frame(top_frame, bg='azure2', width=300, height=270)
        ctr_mid = tk.Frame(top_frame, bg='mint cream', width=340, height=270, padx=3, pady=3)
        ctr_right = tk.Frame(top_frame, bg='LightCyan2', width=700, height=270, padx=3, pady=3)
        ctr_left.grid(row=0, column=0, sticky="nsew")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_right.grid(row=0, column=2, sticky="nsew")

        # create the center frame widgets
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=1)
        ctr_mid_left = tk.Frame(center, bg='white', width=300, height=340, padx=3, pady=3)
        ctr_mid_mid = tk.Frame(center, bg='white', width=340, height=340, padx=3, pady=3)
        ctr_mid_right = tk.Frame(center, bg='white', width=700, height=340, padx=3, pady=3)
        ctr_mid_left.grid(row=1, column=0, sticky="nsew")
        ctr_mid_mid.grid(row=1, column=1, sticky="nsew")
        ctr_mid_right.grid(row=1, column=2, sticky="nsew")

 
        model_label = tk.Label(ctr_mid, text='Free Parameters', font=("Helvetica", 16), anchor=tk.W, justify=tk.LEFT, bg='mint cream')
        label1 = tk.Label(ctr_mid, text='UD Learning Rate:', bg='mint cream', anchor=tk.W)
        label2 = tk.Label(ctr_mid, text='EB Learning Rate:', bg='mint cream')
        label3 = tk.Label(ctr_mid, text='RB Learning Rate:', bg='mint cream')
        label4 = tk.Label(ctr_mid, text='Exploration Level:', bg='mint cream')
        label5 = tk.Label(ctr_mid, text='NP Arm Bias:', bg='mint cream')
        #label6 = Label(ctr_mid, text='Cost Ratio (C/I):', bg='mint cream')
        label6 = tk.Label(ctr_mid, text='Number of Trials:', bg='mint cream')

        self.v = [tk.StringVar(ctr_mid, value='0.002'), tk.StringVar(ctr_mid, value='0.01'), 
            tk.StringVar(ctr_mid, value='0.1'), tk.StringVar(ctr_mid, value='10'),
            tk.StringVar(ctr_mid, value='0.2'), tk.StringVar(ctr_mid, value='2')]
        self.entry1 = tk.Entry(ctr_mid, textvariable=self.v[0], background="LightBlue3", width=6)
        self.entry2 = tk.Entry(ctr_mid, textvariable=self.v[1], background="LightBlue3", width=6)
        self.entry3 = tk.Entry(ctr_mid, textvariable=self.v[2], background="LightBlue3", width=6)
        self.entry4 = tk.Entry(ctr_mid, textvariable=self.v[3], background="LightBlue3", width=6)
        self.entry5 = tk.Entry(ctr_mid, textvariable=self.v[4], background="LightBlue3", width=6)
        #self.entry6 = Entry(ctr_mid, background="LightBlue3", width=6)
        self.entry6 = tk.Entry(ctr_mid, textvariable=self.v[5], background="LightBlue2", width=6)
        
        run_button = tk.Button(ctr_mid, text="RUN SIMULATION", bg="red", command=self.runSimulation)
        
        # create the widgets for the top frame: SAVE PARAMETERS
        save_button = tk.Button(ctr_left, text="SAVE", bg="red", command=self.save)
        save_button.grid(row=5, column=3)
        saveas_button = tk.Button(ctr_left, text="SAVE AS", bg="red", command=self.file_save)
        saveas_button.grid(row=10, column=3)

        # layout the widgets in the top frame
        model_label.grid(row=0, column=3, columnspan=30)
        label1.grid(row=1, column=1)
        label2.grid(row=2, column=1)
        label3.grid(row=3, column=1)
        label4.grid(row=4, column=1)
        label5.grid(row=5, column=1)
        #label6.grid(row=6, column=1)
        label6.grid(row=6, column=1)
        self.entry1.grid(row=1, column=3)
        self.entry2.grid(row=2, column=3)
        self.entry3.grid(row=3, column=3)
        self.entry4.grid(row=4, column=3)
        self.entry5.grid(row=5, column=3)
        #entry6.grid(row=6, column=3)
        self.entry6.grid(row=6, column=3)
        #run_button.pack(side="bottom")
        run_button.grid(row=10, column=3)

        # layout top Left
        #photo = PhotoImage(file="test.gif", width=300)
        #w = Label(ctr_left, image=photo)
        #w.photo = photo
        #w.pack()

        #List of trials IDs for plotting
        x = np.arange(0, int(self.entry6.get()), 1)

        #Setting the bottom dashboard canvas
        self.fig = Figure(figsize=(3.2,3.4))
        self.fig.suptitle('Sensitivities')
        self.fig.patch.set_facecolor('white')
        ax = self.fig.add_subplot(111)
        ax.patch.set_facecolor('lightgray')
        ax.patch.set_alpha(0.2)
        ax.tick_params(axis='both', which='major', labelsize=9)
        self.line, = ax.plot(x, [0] * int(self.entry6.get()))
        self.canvas = FigureCanvasTkAgg(self.fig, master=ctr_mid_left)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=0)

        self.fig2 = Figure(figsize=(3.2,3.4))
        self.fig2.suptitle('Probabilities')
        self.fig2.patch.set_facecolor('white')
        ax2 = self.fig2.add_subplot(111)
        ax2.patch.set_facecolor('lightgray')
        ax2.patch.set_alpha(0.2)
        ax2.tick_params(axis='both', which='major', labelsize=9)
        self.line2, = ax2.plot(x, [0] * int(self.entry6.get()), color='green')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=ctr_mid_mid)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side='bottom', fill='both', expand=0)

        self.fig3 = Figure(figsize=(8.2,3.4))
        self.fig3.suptitle('Accuracy')
        self.fig3.patch.set_facecolor('white')
        ax3 = self.fig3.add_subplot(111)
        ax3.patch.set_facecolor('lightgray')
        ax3.patch.set_alpha(0.2)
        ax3.tick_params(axis='both', which='major', labelsize=9)
        self.line3, = ax3.plot(x, [0] * int(self.entry6.get()), color='green')
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=ctr_mid_right)
        self.canvas3.get_tk_widget().grid(column=0,row=1)
        self.canvas3.draw()
        #self.canvas3.get_tk_widget().pack(side='bottom', fill='both', expand=0)

        

        #self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


    def initAnim(self):  # only required for blitting to give a clean slate.
        self.line3.set_ydata([np.nan] * int(self.entry6.get()))
        return self.line3,

    def animate(self, trialNum, rt, errorLeft_angle, errorRight_angle):
        x, y = self.line.get_data()
        self.line.set_ydata(rt)
        self.line.set_xdata(np.arange(0, trialNum+1, 1))
        self.canvas.draw()

        x, y = self.line2.get_data()
        self.line2.set_ydata(errorLeft_angle)
        self.line2.set_xdata(np.arange(0, trialNum+1, 1))
        self.canvas2.draw()

        x, y = self.line3.get_data()
        self.line3.set_ydata(errorRight_angle)
        self.line3.set_xdata(np.arange(0, trialNum+1, 1))
        self.canvas3.draw()

    def drawTrialData(self, trialNum, rt, errorLeft_angle, errorRight_angle, expected_L, expected_R, energy_L, energy_R, angle_per_trial):

        #ani = animation.FuncAnimation(self.fig, self.animate(trialNum, rt, errorLeft_angle, errorRight_angle), init_func=self.initAnim, interval=2, blit=True, save_count=50)
        #ani = animation.FuncAnimation(self.fig2, self.animate(trialNum, rt, errorLeft_angle, errorRight_angle), init_func=self.initAnim, interval=2, blit=True, save_count=50)
        ani = animation.FuncAnimation(self.fig3, self.animate(trialNum, rt, errorLeft_angle, errorRight_angle), init_func=self.initAnim, interval=20, blit=False)
        plt.show()

    def runSimulation(self):

        SimulationsMain(self, float(self.entry1.get()), float(self.entry2.get()), float(self.entry3.get()), float(self.entry4.get()), float(self.entry5.get()), int(self.entry6.get()))
        # new_frame = frame_class(self)
        # if self._frame is not None:
        #     self._frame.destroy()
        # self._frame = new_frame
        # self._frame.pack()

    def save(self):
        if self.f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            self.file_save()
        else:
            f = open(self.f.name, 'wb')
            for item in self.v:
                f.write("%s\n" % item.get())        
            f.close()

    def file_save(self):
        self.f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        f=self.f
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        for item in self.v:
            f.write("%s\n" % item.get())
        f.close()

    def file_open(self):
        """open a file to read"""
        # optional initial directory (default is current directory)
        initial_dir = "/"
        # the filetype mask (default is all files)
        mask = \
        [("Text and Python files","*.txt *.py *.pyw"), 
        ("HTML files","*.htm"), 
        ("All files","*.*")]        
        fin = askopenfile(initialdir=initial_dir, filetypes=mask, mode='r')
        text = fin.read()
        if text != None:
            self.text.delete(0.0, END)
            self.text.insert(END,text)
