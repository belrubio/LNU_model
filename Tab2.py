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
import plot as pl
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import time
from numpy.random import random
from PIL import Image, ImageTk


# Notebook - Tab 2
class Tab2(tk.Frame):
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
        center = tk.Frame(self, bg='gray97', width=1360, height=600, padx=3, pady=3)
        btm_frame = tk.Frame(self, bg='gray97', width=1360, height=80, pady=3)

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
        ctr_left = tk.Frame(top_frame, bg='azure2', width=300, height=270, padx=3, pady=3)
        ctr_mid = tk.Frame(top_frame, bg='mint cream', width=340, height=270, padx=3, pady=3)
        ctr_preright = tk.Frame(top_frame, bg='LightCyan2', width=400, height=270, padx=3, pady=3)
        ctr_right = tk.Frame(top_frame, bg='LightCyan2', width=300, height=270, padx=3, pady=3)
        ctr_left.grid(row=0, column=0, sticky="nsew")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_preright.grid(row=0, column=2, sticky="nsew")
        ctr_right.grid(row=0, column=3, sticky="nsew")
        ctr_right.configure(width=500)

        # Tell pygame's SDL window which window ID to use    
        #os.environ['SDL_WINDOWID'] = str(ctr_right.winfo_id())

        # create the center frame widgets
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=1)
        self.ctr_mid_mid = tk.Frame(center, bg='white', width=640, height=400, padx=3, pady=3)
        self.ctr_mid_right = tk.Frame(center, bg='mint cream', width=700, height=400, padx=3, pady=3)
        self.ctr_mid_mid.grid(row=1, column=1, sticky="nsew")
        self.ctr_mid_right.grid(row=1, column=2, sticky="nsew")

 
        model_label = tk.Label(ctr_mid, text='Free Parameters', font=("Helvetica", 16), anchor=tk.W, justify=tk.LEFT, bg='mint cream')
        label1 = tk.Label(ctr_mid, text='UD Learning Rate:', bg='mint cream', anchor=tk.W)
        label2 = tk.Label(ctr_mid, text='EB Learning Rate:', bg='mint cream')
        label3 = tk.Label(ctr_mid, text='RB Learning Rate:', bg='mint cream')
        label4 = tk.Label(ctr_mid, text='Exploration Level:', bg='mint cream')
        label5 = tk.Label(ctr_mid, text='NP Arm Bias:', bg='mint cream')
        #label6 = Label(ctr_mid, text='Cost Ratio (C/I):', bg='mint cream')
        label6 = tk.Label(ctr_mid, text='Number of Trials:', bg='mint cream')
        label7 = tk.Label(ctr_mid, text='Show trials at:', bg='mint cream')

        self.v = [tk.StringVar(ctr_mid, value='0.002'), tk.StringVar(ctr_mid, value='0.01'), 
            tk.StringVar(ctr_mid, value='0.1'), tk.StringVar(ctr_mid, value='10'),
            tk.StringVar(ctr_mid, value='0.2'), tk.StringVar(ctr_mid, value='2'), tk.StringVar(ctr_mid, value='100'), tk.StringVar(ctr_mid, value='100')]
        self.entry1 = tk.Entry(ctr_mid, textvariable=self.v[0], background="LightBlue3", width=6)
        self.entry2 = tk.Entry(ctr_mid, textvariable=self.v[1], background="LightBlue3", width=6)
        self.entry3 = tk.Entry(ctr_mid, textvariable=self.v[2], background="LightBlue3", width=6)
        self.entry4 = tk.Entry(ctr_mid, textvariable=self.v[3], background="LightBlue3", width=6)
        self.entry5 = tk.Entry(ctr_mid, textvariable=self.v[4], background="LightBlue3", width=6)
        #self.entry6 = Entry(ctr_mid, background="LightBlue3", width=6)
        self.entry6 = tk.Entry(ctr_mid, textvariable=self.v[5], background="LightBlue2", width=6)
        self.entry7 = tk.Entry(ctr_mid, textvariable=self.v[6], background="LightBlue2", width=6)
        self.entry8 = tk.Entry(ctr_mid, textvariable=self.v[7], background="LightBlue2", width=6)

        run_button = tk.Button(ctr_mid, text="RUN SIMULATION", bg="red", command=self.runSimulation)

        # create the widgets for the top frame: SAVE PARAMETERS
        save_button = tk.Button(ctr_left, text="SAVE", bg="red", command=self.save)
        save_button.grid(row=5, column=3)
        saveas_button = tk.Button(ctr_left, text="SAVE AS", bg="red", command=self.file_save)
        saveas_button.grid(row=10, column=3)
        self.progressbar = ttk.Progressbar(btm_frame, style='text.Horizontal.TProgressbar', orient = 'horizontal', length=600, mode='determinate')        
        self.progressbar.pack(fill=tk.BOTH, side=tk.TOP)
        self.progressbar["value"] = 0
        
        about = "Ballester, B. R., Maier, M., Mozo, R. M. S. S., Castaneda, V., Duff, A., and Verschure, P. F. (2016). Counteracting learned non-use in chronic stroke patients with reinforcement-induced movement therapy. Journal of neuroengineering and rehabilitation, 13(1), 74.\n SPECS Lab, IBEC. Contact: brubio@ibecbarcelona.eu\n"
        T = tk.Label(btm_frame, text=about, font=("Helvetica", 12), bg='gray97')
        T.pack()

        self.style = ttk.Style(self)
        # add label in the layout
        self.style.layout('text.Horizontal.TProgressbar', 
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar',
                                      {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}), 
                      ('Horizontal.Progressbar.label', {'sticky': ''})])
        # set initial text
        self.style.configure('text.Horizontal.TProgressbar', text='0')

        # layout the widgets in the top frame
        model_label.grid(row=0, column=3)
        label1.grid(row=1, column=1)
        label2.grid(row=2, column=1)
        label3.grid(row=3, column=1)
        label4.grid(row=4, column=1)
        label5.grid(row=5, column=1)
        label6.grid(row=6, column=1)
        label7.grid(row=7, column=1)
        self.entry1.grid(row=1, column=3)
        self.entry2.grid(row=2, column=3)
        self.entry3.grid(row=3, column=3)
        self.entry4.grid(row=4, column=3)
        self.entry5.grid(row=5, column=3)
        self.entry6.grid(row=6, column=3)
        self.entry7.grid(row=7, column=3)
        self.entry8.grid(row=7, column=4)
        run_button.grid(row=10, column=3)

        # layout top center show image?
        # image = tk.PhotoImage(file='ModelOverview.gif')        
        # cwgt=tk.Canvas(ctr_preright, width = 620, height = 300)
        # cwgt.pack(expand=True, fill=tk.BOTH)
        # # keep a link to the image to stop the image being garbage collected
        # cwgt.img=image
        # cwgt.create_image(0, 0, anchor=tk.NW, image=image)


        self.labelR1= tk.Label(ctr_right, text='Final State                           ', font=("Helvetica", 16), anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR2= tk.Label(ctr_right, text='P(R Hand selection): -', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR3= tk.Label(ctr_right, text='Mean error R: -              ', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR4= tk.Label(ctr_right, text='Mean error L: -', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR5= tk.Label(ctr_right, text='Mean cost R: -', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR6= tk.Label(ctr_right, text='Mean cost L: -', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR7= tk.Label(ctr_right, text='Mean EReward R: -', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR8= tk.Label(ctr_right, text='Mean EReward L: -', anchor=tk.W, justify=tk.LEFT, bg='LightCyan2')
        self.labelR1.grid(row=1, column=1, sticky=tk.W)
        self.labelR2.grid(row=2, column=1, sticky=tk.W)
        self.labelR3.grid(row=3, column=1, sticky=tk.W)
        self.labelR4.grid(row=4, column=1, sticky=tk.W)
        self.labelR5.grid(row=5, column=1, sticky=tk.W)
        self.labelR6.grid(row=6, column=1, sticky=tk.W)
        self.labelR7.grid(row=7, column=1, sticky=tk.W)
        self.labelR8.grid(row=8, column=1, sticky=tk.W)


    def drawTrialData(self, trialNum, rt, angle_per_trial, listOfAngles, probability_right, probability_left, error_right, error_left, error_extent_left, error_extent_right, expectedRewardLeft, expectedRewardRight, energy_R, energy_L, sensit_R, sensit_L):

        self.labelR2["text"] = 'P(R Hand selection): ' + str(round(sum(x>0.5 for x in probability_right),3))
        self.labelR3["text"] = 'Mean error R: ' + str(round(np.mean(error_right),3))
        self.labelR4["text"] = 'Mean error L: ' + str(round(np.mean(error_left),3))
        self.labelR5["text"] = 'Mean cost R: ' + str(round(np.mean(energy_R),3))
        self.labelR6["text"] = 'Mean cost L: ' + str(round(np.mean(energy_L),3))
        self.labelR7["text"] = 'Mean EReward R: -' + str(round(np.mean(expectedRewardRight),3))
        self.labelR8["text"] = 'Mean EReward L: -' + str(round(np.mean(expectedRewardLeft),3))

        #titlePanel1 = "Performance descriptors \n"
        #T1 = tk.Label(self.ctr_mid_mid, text=titlePanel1, font=("Helvetica", 16), bg='gray97')
        #T1.pack(side='top', expand=True)

        #Setting the bottom dashboard canvas
        self.fig = Figure(figsize=(2.4,3.6))
        self.fig.suptitle('\nError direction\n')
        self.fig.patch.set_facecolor('white')
        ax = self.fig.add_subplot(111, polar=True)
        ax.patch.set_facecolor('lightgray')
        ax.patch.set_alpha(0.2)
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.set_yticklabels([])
        ax.plot(np.radians(listOfAngles), energy_L, 'b', linewidth=1, linestyle='solid')  
        ax.plot(np.radians(listOfAngles), energy_R, 'r', linewidth=1, linestyle='solid')
        ax.fill(np.radians(listOfAngles), energy_L, 'b', alpha=0.1)
        ax.fill(np.radians(listOfAngles), energy_R, 'r', alpha=0.1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.ctr_mid_mid)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='left', fill='y', expand=True)

        #Setting the bottom dashboard canvas
        self.fig2 = Figure(figsize=(2.4,3.6))
        self.fig2.suptitle('\nProbabilities\n')
        self.fig2.patch.set_facecolor('white')
        ax2 = self.fig2.add_subplot(111, polar=True)
        ax2.patch.set_facecolor('lightgray')
        ax2.patch.set_alpha(0.2)
        ax2.tick_params(axis='both', which='major', labelsize=9)
        ax2.set_yticklabels([])
        ax2.plot(np.radians(listOfAngles), probability_left, 'b', linewidth=1, linestyle='solid')  
        ax2.plot(np.radians(listOfAngles), probability_right, 'r', linewidth=1, linestyle='solid')
        ax2.fill(np.radians(listOfAngles), probability_left, 'b', alpha=0.1)
        ax2.fill(np.radians(listOfAngles), probability_right, 'r', alpha=0.1)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.ctr_mid_mid)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side='left', fill='y', expand=True)

        #Setting the bottom dashboard canvas
        self.fig3 = Figure(figsize=(2.4,3.6))
        self.fig3.suptitle('\nExpected Reward\n')
        self.fig3.patch.set_facecolor('white')
        ax3 = self.fig3.add_subplot(111, polar=True)
        ax3.patch.set_facecolor('lightgray')
        ax3.patch.set_alpha(0.2)
        ax3.tick_params(axis='both', which='major', labelsize=9)
        # Draw one axe per variable + add labels
        #ax3.xticks(listOfAngles[:-1], ['Left', 'Right']], color='grey', size=8)
        # Draw ylabels
        #ax3.set_rlabel_position(0)
        #plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
        #plt.ylim(0,40)
        # Plot data
        ax3.plot(np.radians(listOfAngles), expectedRewardLeft, 'b', linewidth=1, linestyle='solid')  
        ax3.plot(np.radians(listOfAngles), expectedRewardRight, 'r', linewidth=1, linestyle='solid')
        ax3.set_yticklabels([])

        # Fill area
        ax3.fill(np.radians(listOfAngles), expectedRewardLeft, 'b', alpha=0.1)
        ax3.fill(np.radians(listOfAngles), expectedRewardRight, 'r', alpha=0.1)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.ctr_mid_mid)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().pack(side='left', fill='y', expand=True)
 
        #titlePanel2 = "Distribution of Direction-tuned \n cells in Motor cortex"
        #T2 = tk.Label(self.ctr_mid_right, text=titlePanel2, font=("Helvetica", 16), bg='gray97')
        #T2.pack(side='top', expand=True)

        #windrose like a stacked histogram with normed (displayed in percent) results
        fig4 = plt.figure(figsize=(2.4,3.2), dpi=80, facecolor='w', edgecolor='w')
        fig4.patch.set_facecolor('white')
        fig4.suptitle('\nDirection-tuned cells\n Left Cortex')
        ax4 = fig4.add_subplot(111, polar=True)
        ax4.patch.set_facecolor('lightgray')
        ax4.patch.set_alpha(0.2)
        ax4.tick_params(axis='both', which='major', labelsize=9)
        ax4.set_yticklabels([])
        wd = sensit_R
        ws = np.arange((2*np.pi)/24,(2*np.pi),(2*np.pi)/12)
        DataHist, bins = np.histogram(sensit_R, bins=12, density=True)
        bars = ax4.bar(ws, DataHist, width=(2*np.pi)/14, bottom=0)

        # Use custom colors and opacity
        for r, bar in zip(DataHist, bars):
            bar.set_facecolor(plt.cm.jet(r / 10.))
            bar.set_alpha(0.8)

        self.canvas4 = FigureCanvasTkAgg(fig4, master=self.ctr_mid_right)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().pack(side='left', fill='both', expand=True)       
        
        #windrose like a stacked histogram with normed (displayed in percent) results
        fig5 = plt.figure(figsize=(2.4,3.2), dpi=80, facecolor='w', edgecolor='w')
        fig5.suptitle('\nDirection-tuned cells\n Right Cortex')
        fig5.patch.set_facecolor('white')
        ax5 = fig5.add_subplot(111, polar=True)
        ax5.patch.set_facecolor('lightgray')
        ax5.patch.set_alpha(0.2)
        ws = np.arange((2*np.pi)/24,(2*np.pi),(2*np.pi)/12)
        DataHist, bins = np.histogram(sensit_L, bins=12, density=True)
        bars2 = ax5.bar(ws, DataHist, width=(2*np.pi)/14, bottom=0)
        ax5.tick_params(axis='both', which='major', labelsize=9)
        ax5.set_yticklabels([])

        # Use custom colors and opacity
        for r, bar in zip(DataHist, bars2):
            bar.set_facecolor(plt.cm.jet(r *400.))
            bar.set_alpha(0.8)

        self.canvas5 = FigureCanvasTkAgg(fig5, master=self.ctr_mid_right)
        self.canvas5.draw()
        self.canvas5.get_tk_widget().pack(side='left', fill='both', expand=True)
        #plt.show()

    def runSimulation(self):

        done = SimulationsMain(self, float(self.entry1.get()), float(self.entry2.get()), float(self.entry3.get()), float(self.entry4.get()), float(self.entry5.get()), int(self.entry6.get()), int(self.entry7.get()), int(self.entry8.get()), False)

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

    def play_trial(self, armAngleG= 0, foreArmAngleG = 0, targetXG = 0 ,targetYG =0  , selectedHand=-1, acR=0, acL=0, pacR=0, pacL=0, ac=0, expR_R=0, expR_L=0, startTime=0, currentT=0, trialNow=0, flag=False):
        if (trialNow==int(self.entry7.get())+5) or (trialNow==int(self.entry8.get())+5):
            pl.close_gui()
        else:
            ac, pacR, pacL = pl.gui(armAngleG, foreArmAngleG, targetXG ,targetYG  , selectedHand, acR, acL, pacR, pacL, ac, expR_R, expR_L, startTime, currentT)
        
        return ac, pacR, pacL
        
    # def plotPolar(self, Figure, title, frame, var1, var2):
 
