from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import matplotlib.pyplot as plt
import tkinter as tk
import ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox
import numpy as np
from numpy.random import random
from scipy import stats
import plot as pl
from runSimulations import *


# Notebook - Tab
class tabGUI(tk.Frame):
    def __init__(self, master, phase):
        tk.Frame.__init__(self, master)

        # Get values for fields depending on phase (Training, Stroke...)
        self.simulateStroke = self.getStrokeProtocol(phase)
        self.simulateRehab = self.getRehabProtocol(phase)
        self.simulateFU = self.getFuProtocol(phase)
        self.entryFields = self.getEntryFields(phase)

        # Vars for plotting
        self.data1 = []
        self.data2 = []
        self.data3 = []
        self.f = None

        # layout all of the main containers
        top_frame = tk.Frame(self, bg='gray97', width=1360, height=10, pady=3)
        self.center = tk.Frame(
            self, bg='gray97', width=1360, height=600, padx=3, pady=3)
        btm_frame = tk.Frame(self, bg='gray97', width=1360, height=80, pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="nsew")
        self.center.grid(row=1, sticky="ew")
        btm_frame.grid(row=2, sticky="nsew")

        # create the top frame widgets
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        ctr_left = tk.Frame(
            top_frame, bg='azure2', width=300, height=270, padx=3, pady=3)
        ctr_mid = tk.Frame(
            top_frame, bg='mint cream', width=340, height=270, padx=3, pady=3)
        ctr_preright = tk.Frame(
            top_frame, bg='LightCyan2', width=400, height=270, padx=3, pady=3)
        ctr_right = tk.Frame(
            top_frame, bg='LightCyan2', width=300, height=270, padx=3, pady=3)
        ctr_left.grid(row=0, column=0, sticky="nsew")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_preright.grid(row=0, column=2, sticky="nsew")
        ctr_right.grid(row=0, column=3, sticky="nsew")
        ctr_right.configure(width=500)

        # create the center frame widgets
        self.center.grid_rowconfigure(0, weight=1)
        self.center.grid_columnconfigure(1, weight=1)

        # define style of the main frames
        self.ctr_mid_mid = tk.Frame(
            self.center, bg='white', width=640, height=400, padx=3, pady=3)
        self.ctr_mid_right = tk.Frame(
            self.center,
            bg='mint cream',
            width=700,
            height=400,
            padx=3,
            pady=3)
        self.ctr_mid_mid.grid(row=1, column=1, sticky="nsew")
        self.ctr_mid_right.grid(row=1, column=2, sticky="nsew")

        # define style for labels
        model_label = tk.Label(
            ctr_mid,
            text=self.entryFields[0],
            font=("Helvetica", 16),
            anchor=tk.W,
            justify=tk.LEFT,
            bg='mint cream')
        self.labels = []
        for i in range(len(self.entryFields) - 1):
            self.labels.append(
                tk.Label(
                    ctr_mid,
                    text=self.entryFields[i + 1],
                    bg='mint cream',
                    anchor=tk.W))

        # define default values for the entries (free parameters)
        self.v = [
            tk.StringVar(ctr_mid, value='0.002'),
            tk.StringVar(ctr_mid, value='0.01'),
            tk.StringVar(ctr_mid, value='0.1'),
            tk.StringVar(ctr_mid, value='10'),
            tk.StringVar(ctr_mid, value='0.2'),
            tk.StringVar(ctr_mid, value='2'),
            tk.StringVar(ctr_mid, value='100'),
            tk.StringVar(ctr_mid, value='100'),
            tk.StringVar(ctr_mid, value='0'),
            tk.StringVar(ctr_mid, value='0'),
            tk.StringVar(ctr_mid, value='0')
        ]
        self.entries = []
        for i in range(len(self.entryFields) - 1):
            self.entries.append(
                tk.Entry(
                    ctr_mid,
                    textvariable=self.v[i],
                    background="LightBlue3",
                    width=6))


        run_button = tk.Button(
            ctr_mid,
            text="RUN SIMULATION",
            bg="red",
            command=self.startSimulation)

        # create the widgets for the top-left frame: SAVE/QUIT buttons
        save_button = tk.Button(
            ctr_left, text="SAVE", bg="red", command=self.save)
        save_button.grid(row=5, column=3)
        saveas_button = tk.Button(
            ctr_left, text="SAVE AS", bg="red", command=self.file_save)
        saveas_button.grid(row=10, column=3)
        self.progressbar = ttk.Progressbar(
            btm_frame,
            style='text.Horizontal.TProgressbar',
            orient='horizontal',
            length=600,
            mode='determinate')
        self.progressbar.pack(fill=tk.BOTH, side=tk.TOP)
        self.progressbar["value"] = 0

        about = "Ballester, B. R., Maier, M., Mozo, R. M. S. S., Castaneda, V., Duff, A., and Verschure, P. F. (2016). Counteracting learned non-use in chronic stroke patients with reinforcement-induced movement therapy. Journal of neuroengineering and rehabilitation, 13(1), 74.\n SPECS Lab, IBEC. Contact: brubio@ibecbarcelona.eu\n"
        T = tk.Label(
            btm_frame, text=about, font=("Helvetica", 12), bg='gray97')
        T.pack()

        # Display a progress bar on the bottom frame
        self.style = ttk.Style(self)
        # add label in the layout fo the progress bar
        self.style.layout('text.Horizontal.TProgressbar',
                          [('Horizontal.Progressbar.trough', {
                              'children': [('Horizontal.Progressbar.pbar', {
                                  'side': 'left',
                                  'sticky': 'ns'
                              })],
                              'sticky':
                              'nswe'
                          }), ('Horizontal.Progressbar.label', {
                              'sticky': ''
                          })])
        # set initial text
        self.style.configure('text.Horizontal.TProgressbar', text='0')

        # layout the widgets in the top frame
        model_label.grid(row=0, column=3)

        for i in range(len(self.labels)):
            self.labels[i].grid(row=i + 1, column=1)
            if (i == 7):
                self.labels[i].grid(row=i, column=4)
            if (i > 7):
                self.labels[i].grid(row=i - 7, column=5)

        for i in range(len(self.entries)):
            self.entries[i].grid(row=i + 1, column=3)
            if (i == 7):
                self.entries[i].grid(row=i, column=5)
            if (i > 7):
                self.entries[i].grid(row=i - 7, column=6)

        run_button.grid(row=9, column=3, sticky="sew")

        # Define labels for the entry fields
        self.labelR1 = tk.Label(
            ctr_right,
            text='Final State                           ',
            font=("Helvetica", 16),
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR2 = tk.Label(
            ctr_right,
            text='P(R Hand selection): -',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR3 = tk.Label(
            ctr_right,
            text='Mean error L hand: -              ',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR4 = tk.Label(
            ctr_right,
            text='Mean error R hand: -',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR5 = tk.Label(
            ctr_right,
            text='Mean cost L hand: -',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR6 = tk.Label(
            ctr_right,
            text='Mean cost R hand: -',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR7 = tk.Label(
            ctr_right,
            text='Mean EReward L hand: -',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR8 = tk.Label(
            ctr_right,
            text='Mean EReward R hand: -',
            anchor=tk.W,
            justify=tk.LEFT,
            bg='LightCyan2')
        self.labelR1.grid(row=1, column=1, sticky=tk.W)
        self.labelR2.grid(row=2, column=1, sticky=tk.W)
        self.labelR3.grid(row=3, column=1, sticky=tk.W)
        self.labelR4.grid(row=4, column=1, sticky=tk.W)
        self.labelR5.grid(row=5, column=1, sticky=tk.W)
        self.labelR6.grid(row=6, column=1, sticky=tk.W)
        self.labelR7.grid(row=7, column=1, sticky=tk.W)
        self.labelR8.grid(row=8, column=1, sticky=tk.W)

    # Plot de results from simulations
    def drawTrialData(self, trialNum, rt, angle_per_trial, listOfAngles,
                      probability_right, probability_left, error_right,
                      error_left, error_extent_left, error_extent_right,
                      expectedRewardLeft, expectedRewardRight, energy_R,
                      energy_L, sensit_R, sensit_L):

        self.labelR2["text"] = 'P(R Hand selection): ' + str(
            round(np.mean(probability_right), 3))
        self.labelR3["text"] = 'Mean error L hand: ' + str(
            round(np.mean(error_right) * 100, 3))
        self.labelR4["text"] = 'Mean error R hand: ' + str(
            round(np.mean(error_left) * 100, 3))
        self.labelR5["text"] = 'Mean cost L hand: ' + str(
            round(np.mean(energy_R), 3))
        self.labelR6["text"] = 'Mean cost R hand: ' + str(
            round(np.mean(energy_L), 3))
        self.labelR7["text"] = 'Mean EReward L hand: ' + str(
            round(np.mean(expectedRewardRight), 3))
        self.labelR8["text"] = 'Mean EReward R hand: ' + str(
            round(np.mean(expectedRewardLeft), 3))

        self.ctr_mid_mid.destroy()
        self.ctr_mid_right.destroy()

        self.ctr_mid_mid = tk.Frame(
            self.center, bg='white', width=640, height=400, padx=3, pady=3)
        self.ctr_mid_right = tk.Frame(
            self.center,
            bg='mint cream',
            width=700,
            height=400,
            padx=3,
            pady=3)
        self.ctr_mid_mid.grid(row=1, column=1, sticky="nsew")
        self.ctr_mid_right.grid(row=1, column=2, sticky="nsew")

        # Setting the middle dashboard canvas for plotting
        # Figure 1
        self.fig = Figure(figsize=(2.4, 3.6))
        self.fig.suptitle('\nCost\n')
        self.fig.patch.set_facecolor('white')
        ax = self.fig.add_subplot(111, polar=True)
        ax.patch.set_facecolor('lightgray')
        ax.patch.set_alpha(0.2)
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.set_yticklabels([])
        ax.plot(
            np.radians(listOfAngles),
            energy_L,
            'r',
            linewidth=1,
            linestyle='solid')
        ax.plot(
            np.radians(listOfAngles),
            energy_R,
            'b',
            linewidth=1,
            linestyle='solid')
        ax.fill(np.radians(listOfAngles), energy_L, 'r', alpha=0.1)
        ax.fill(np.radians(listOfAngles), energy_R, 'b', alpha=0.1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.ctr_mid_mid)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='left', fill='y', expand=True)

        # Figure 2
        self.fig2 = Figure(figsize=(2.4, 3.6))
        self.fig2.suptitle('\nProbabilities\n')
        self.fig2.patch.set_facecolor('white')
        ax2 = self.fig2.add_subplot(111, polar=True)
        ax2.patch.set_facecolor('lightgray')
        ax2.patch.set_alpha(0.2)
        ax2.tick_params(axis='both', which='major', labelsize=9)
        ax2.set_yticklabels([])
        ax2.plot(
            np.radians(listOfAngles),
            probability_left,
            'b',
            linewidth=1,
            linestyle='solid')
        ax2.plot(
            np.radians(listOfAngles),
            probability_right,
            'r',
            linewidth=1,
            linestyle='solid')
        ax2.fill(np.radians(listOfAngles), probability_left, 'b', alpha=0.1)
        ax2.fill(np.radians(listOfAngles), probability_right, 'r', alpha=0.1)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.ctr_mid_mid)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side='left', fill='y', expand=True)

        binSet = np.degrees(
            np.append(
                np.arange(0, (2 * np.pi), (2 * np.pi) / 12), [(2 * np.pi)]))

        # Figure 3
        self.fig3 = Figure(figsize=(2.4, 3.6))
        self.fig3.suptitle('\nExpected Reward\n')
        self.fig3.patch.set_facecolor('white')
        ax3 = self.fig3.add_subplot(111, polar=True)
        ax3.patch.set_facecolor('lightgray')
        ax3.patch.set_alpha(0.2)
        ax3.tick_params(axis='both', which='major', labelsize=9)
        ws = np.arange((2 * np.pi) / 24, (2 * np.pi), (2 * np.pi) / 12)
        bin_meansL = []
        bin_meansR = []
        bin_meansL, bin_edges, binnumber = stats.binned_statistic(
            np.radians(listOfAngles),
            expectedRewardLeft,
            statistic='mean',
            bins=12)

        bin_meansR, bin_edges, binnumber = stats.binned_statistic(
            np.radians(listOfAngles),
            expectedRewardRight,
            statistic='mean',
            bins=12)

        ax3.set_yticklabels([])
        # Fill area
        ax3.fill(ws, bin_meansL, 'r', alpha=0.2)
        ax3.fill(ws, bin_meansR, 'b', alpha=0.2)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.ctr_mid_mid)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().pack(side='left', fill='y', expand=True)

        # Figure 4
        # Wind-rose like a stacked histogram with normed results (in percent)
        self.fig4 = plt.figure(
            figsize=(2.4, 3.2), dpi=80, facecolor='w', edgecolor='w')
        self.fig4.patch.set_facecolor('white')
        self.fig4.suptitle('\nDirection-tuned cells\n Left Cortex')
        ax4 = self.fig4.add_subplot(111, polar=True)
        ax4.patch.set_facecolor('lightgray')
        ax4.patch.set_alpha(0.2)
        ax4.tick_params(axis='both', which='major', labelsize=9)
        ax4.set_yticklabels([])
        wd = sensit_R
        ws = np.arange((2 * np.pi) / 24, (2 * np.pi), (2 * np.pi) / 12)
        DataHist, bins = np.histogram(sensit_L, bins=binSet, density=True)
        bars = ax4.bar(ws, DataHist, width=(2 * np.pi) / 14, bottom=0)

        # Use custom colors and opacity
        for r, bar in zip(DataHist, bars):
            bar.set_facecolor(plt.cm.jet(r * 400.))
            bar.set_alpha(0.8)
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=self.ctr_mid_right)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().pack(
            side='left', fill='both', expand=True)

        # Figure 5
        # Wind-rose like a stacked histogram with normed results (in percent)
        self.fig5 = plt.figure(
            figsize=(2.4, 3.2), dpi=80, facecolor='w', edgecolor='w')
        self.fig5.suptitle('\nDirection-tuned cells\n Right Cortex')
        self.fig5.patch.set_facecolor('white')
        ax5 = self.fig5.add_subplot(111, polar=True)
        ax5.patch.set_facecolor('lightgray')
        ax5.patch.set_alpha(0.2)
        ws = np.arange((2 * np.pi) / 24, (2 * np.pi), (2 * np.pi) / 12)
        DataHist, bins = np.histogram(sensit_R, bins=binSet, density=True)
        bars2 = ax5.bar(ws, DataHist, width=(2 * np.pi) / 14, bottom=0)
        ax5.tick_params(axis='both', which='major', labelsize=9)
        ax5.set_yticklabels([])

        # Use custom colors and opacity
        for r, bar in zip(DataHist, bars2):
            bar.set_facecolor(plt.cm.jet(r / 10.))
            bar.set_alpha(0.8)
        self.canvas5 = FigureCanvasTkAgg(self.fig5, master=self.ctr_mid_right)
        self.canvas5.draw()
        self.canvas5.get_tk_widget().pack(
            side='left', fill='both', expand=True)

    # Run the full set of simulations
    def startSimulation(self):
        self.paramsRehab = [0, 0, 0]
        if self.simulateRehab:
            self.paramsRehab[0] = float(self.entries[8].get())
            self.paramsRehab[1] = float(self.entries[9].get())
            self.paramsRehab[2] = float(self.entries[10].get())

        done = runSimulations(self, float(self.entries[0].get()),
                               float(self.entries[1].get()),
                               float(self.entries[2].get()),
                               float(self.entries[3].get()),
                               float(self.entries[4].get()),
                               int(self.entries[5].get()),
                               int(self.entries[6].get()),
                               int(self.entries[7].get()), self.simulateStroke,
                               self.simulateRehab, self.simulateFU,
                               self.paramsRehab[0], self.paramsRehab[1],
                               self.paramsRehab[2])

    # Save the current free paramenters indicated in entry fields
    def save(self):
        if self.f is None:  # return `None` if dialog closed with "cancel".
            self.file_save()
        else:
            f = open(self.f.name, 'wb')
            for item in self.v:
                f.write("%s\n" % item.get())
            f.close()

    # Save AS.. the current free paramenters indicated in entry fields
    def file_save(self):
        self.f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        f = self.f
        if f is None:  # return `None` if dialog closed with "cancel".
            return
        for item in self.v:
            f.write("%s\n" % item.get())
        f.close()

    # Play animation of each trial simulation
    def play_trial(self,
                   armAngleG=0,
                   foreArmAngleG=0,
                   targetXG=0,
                   targetYG=0,
                   selectedHand=-1,
                   acR=0,
                   acL=0,
                   pacR=0,
                   pacL=0,
                   ac=0,
                   expR_R=0,
                   expR_L=0,
                   startTime=0,
                   currentT=0,
                   trialNow=0,
                   flag=False):
        # If this is the 6th trial from onset then stop playing animations
        if (trialNow == int(self.entries[6].get()) + 5) or (
                trialNow == int(self.entries[7].get()) + 5):
            pl.close_gui()
        else:
            # Play trial animation
            ac, pacR, pacL = pl.gui(
                armAngleG, foreArmAngleG, targetXG, targetYG, selectedHand,
                acR, acL, pacR, pacL, ac, expR_R, expR_L, startTime, currentT)

        return ac, pacR, pacL

    def getRehabProtocol(self, phase):
        return {
            'Training': False,
            'Stroke': False,
            'Rehab': True,
            'Followup': False
        }.get(phase, False)

    def getStrokeProtocol(self, phase):
        return {
            'Training': False,
            'Stroke': True,
            'Rehab': False,
            'Followup': False
        }.get(phase, False)

    def getFuProtocol(self, phase):
        return {
            'Training': False,
            'Stroke': False,
            'Rehab': False,
            'Followup': True
        }.get(phase, False)

    # Entry fields to be used in each phase for simulations
    def getEntryFields(self, phase):
        return {
            'Training': [
                'Free Parameters', 'UD Learning Rate:', 'EB Learning Rate:',
                'RB Learning Rate:', 'Exploration Level:', 'NP Arm Bias:',
                'Number of Trials:', 'Show 5 trials at:', '& at'
            ],
            'Stroke': [
                'Free Parameters', 'UD Learning Rate:', 'EB Learning Rate:',
                'RB Learning Rate:', 'Exploration Level:', 'NP Arm Bias:',
                'Number of Trials:', 'Show 5 trials at:', '& at'
            ],
            'Rehab': [
                'Free Parameters', 'UD Learning Rate:', 'EB Learning Rate:',
                'RB Learning Rate:', 'Exploration Level:', 'NP Arm Bias:',
                'Number of Trials:', 'Show 5 trials at:', '& at', 'Force:',
                'Gain:', 'Steer:'
            ],
            'Followup': [
                'Free Parameters', 'UD Learning Rate:', 'EB Learning Rate:',
                'RB Learning Rate:', 'Exploration Level:', 'NP Arm Bias:',
                'Number of Trials:', 'Show 5 trials at:', '& at'
            ]
        }.get(phase, [
            'Free Parameters', 'UD Learning Rate:', 'EB Learning Rate:',
            'RB Learning Rate:', 'Exploration Level:', 'NP Arm Bias:',
            'Number of Trials:', 'Show 5 trials at:', '& at'
        ])
