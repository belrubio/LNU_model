 ----------------------------------------------------------------------------
 2018, Belen Rubio Ballester
 belen.rubio.ballester@gmail.com
 SPECS Lab. Institute of Bioengineering of Catalunya
 Distributed under the terms of the GNU General Public License (GPL-3.0).
 The full license is in the file COPYING.txt, distributed with this software.
 ----------------------------------------------------------------------------
 ## Learned Non-Use Recovery Model

### **Description**

Implementation of a computational functional model of recovery after stroke that establishes a closed loop between arm use, functional recovery, and cortical reorganization (Han et al., 2008; Hidaka et al., 2012; Schweighofer et al., 2009). We extended and applied this model to formulate predictions about the clinical outcome of different therapy combinations based on constraint induced movement therapy and reinforcement. Please, if you reuse this code, reference to: Ballester, Belén Rubio, et al. "Counteracting learned non-use in chronic stroke patients with reinforcement-induced movement therapy." Journal of neuroengineering and rehabilitation 13.1 (2016): 74.

### **Getting Started**

If you are interested in obtaining the program and running it in your machine, you can download an executable file: 
- MAC OSX
- Windows

Please continue reading if you are interested in the source code of this project. The following instructions will get you a copy of the ***Leaned Non-Use Model*** project up and running on your local machine for development and testing purposes.

### Prerequisites

To obtain the source code of the project you will need to either download it from [here](https://github.com/belrubio/LNU_model) or to clone it with:

```
git clone https://github.com/belrubio/LNU_model
```
To run the program from the source code you may need to install some dependencies, such as Pillow and TKinter:

```
pip install pillow
pip install python3-tk

```

## How to Use

The deployment is pretty basic. After running the software a GUI will appear:

![](/images/projects/model/mainWindow.png)

The save buttons on the top left corner will generate a text file and save a list of the values given to the free parameters. Please notice that the free parameters introduced by default correspond with those reported in [Han et al., 2008](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000133) and [Ballester et al., 2016](https://jneuroengrehab.biomedcentral.com/articles/10.1186/s12984-016-0178-x). 

The free parameters are shown on the top left corner refer to:

- UD (0-1): Use-dependent learning rate
- EB (0-1): Error-based learning rate
- RB (0-1): Reinforcement-based learning rate
- EL (0-100): Exploration Level or Noise in the hand selection decision making
- NP (0-1): Non-Paretic Arm Bias/Hand Dominance (currently not used)
- Number of trials: Number of trials to simulate
- show 5 trials at: Trial number onset to play the animation for simulation for 5 consecutive trials.

In the Recovery tab, 3 additional free parameters can be set:

- Force (0-1): a normalized value indicating the probability of forcing the use of the paretic limb at each trial (set it to 0.3 for RIMT administration).
- Gain (0-1): a normalized value indicating the ratio of extent amplification of the paretic limb movement (set it to 0.3 for RIMT administration).
- Steer (0-1): a normalized value indicating the ratio of directional error reduction of the paretic limb movement (set it to 0.7 for RIMT administration).

After introducing all the free parameters, press the button "Run Simulation" and wait until the final state of the model is computed. A window will pop-up to display a set of trials if configured at "Show trials at":

![](/images/projects/model/trialSimulation.png)

When finished, figures will present the data of the simulation:

![](/images/projects/model/simulationsFinished.png)

In addition, three JSON files will be generated:

- Trainned_model_<TAB_NAME>.json
- Trainned_probabilities.json
- Trainned_logs.json

You will find them inside the main folder of the project. These files contain all the data describing the current state of the trained model. The parameters registered in this file include: 

### Trainned_model_"TAB_NAME".json
- The angle sensitivity associated to of each direction tunned neuron in the left cortex
- The angle sensitivity associated to of each direction tunned neuron in the right cortex
- The synaptic weight associated to of each neuron in the left cortex (direction coding network)
- The synaptic weight associated to of each neuron in the right cortex (direction coding network)
- The synaptic weight associated to of each neuron in the left cortex (extent coding network)
- The synaptic weight associated to of each neuron in the right cortex (extent coding network)

### Trainned_probabilities.json
- Probabilities of right-hand selection for each target direction along the 360 degrees.
- Probabilities of left-hand selection for each target direction along the 360 degrees.
- List of target directions.

### Trainned_logs.json
- Hand selected per trial
- Target direction per trial
- Reaction Time per trial
- The error of the left arm's planned movement extent per trial
- The error of the right arm's planned movement extent per trial
- The error of the left arm's planned movement direction per trial
- The error of the right arm's planned movement direction per trial
- Expected reward for the left arm movement per trial
- Expected reward for the right arm movement per trial
- Expected cost for the left arm movement per trial
- Expected cost for the right arm movement per trial
- Actual reward per trial

Notice that a different JSON file of type Trainned_model_"TAB_NAME".json will be generated for each tab after simulations are complete. However, Trainned_probabilities.json and Trainned_logs.json will be overwritten.


## Example

Let's now simulate a case. First, we will simulate a subject with no impairments. We go to tab "Training" and we provide 2,000 trials. At the end of the simulation we will observe a symmetric lateralization in the distribution of direction tunned cells (the two windrose plots on the right):

![](/images/projects/model/training.png)

Now let's move to the tab "Stroke" and let's provide 500 trials after generating a lesion. The results show a lack of cells devoted to the coding of movement directions toward the upper right corner:

![](/images/projects/model/stroke.png)

In the tab Rehabilitation, we can simulate high-intensity Constraint-Induced Movement Therapy (CIMT) by introducing a 0.7 value (normalized scale) in the Field Force. After 2000 trials we observe recovery:

![](/images/projects/model/recovery.png)

Moving to the last tab ("Follow-up") we can simulate an additional trial window of no-therapy. We can introduce 2000 trials to study the stability of the model's state after the rehabilitation treatment:

![](/images/projects/model/followup.png)

## Built With

* [Python](https://www.python.org/) - The programming language used
* [PyGame](https://www.pygame.org/) - A cross-platform set of Python modules designed for writing video games
* [TKinter](https://wiki.python.org/moin/TkInter) - Python's de-facto standard GUI
* [Sublime](https://www.sublimetext.com/) - The editor used


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/belrubio/project/LNU_model). 


## Authors

* **Belén Rubio Ballester** - *Initial work* - [https://www.belenrubioballester.com](https://www.belen.rubio.ballester.com)
* **Diogo Santos Pata** - *Contributor* [https://www.diogosantospata.com](http://www.diogosantospata.com)

## License

This project is licensed under the GNU License v3 - see the [COPYING.txt](https://github.com/belrubio/project/LNU_model/COPYING.txt) file for details.


## Acknowledgments

* Hat tip to anyone whose code was used
* This project was supported by the [cDAC project](https://cordis.europa.eu/project/rcn/192386_en.html).







