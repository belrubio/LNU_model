#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com
# SPECS Lab. Institute for Bioengineering of Catalunya
#
# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#


import numpy as np
import time
import matplotlib.pyplot as plt
from motorCortexNet import *
from actionChoiceNet import *
from choice import *
from armReward import *
from directionCoding import *
import json
import calculateEnergies
import main

energies = [0, 0]
expRewardL = 0
expRewardR = 0


def getDiffAngle(a, b):
    return min(a - b, a - b + 2*np.pi, a - b - 2*np.pi, key=abs)


def runSimulations(UI, UseDependentLearning, ErrorBasedLearning, ReinforcementBasedLearning, Exploration_Level, in_RD, trials, in_showTrial1, in_showTrial2, simulateStroke, simulateRehab, simulateFU, FORCED_TRIAL, GAIN, STEER):
    """Generates simulations,
    when done it plots and saves json files of the final model state.

    Parameters:
        UseDependentLearning (float): Use-dependent learning rate
        ErrorBasedLearning (float): Error-based learning rate
        ReinforcementBasedLearning (float): Reinforcement-based learning rate
        Exploration_Level (float): Exploration Level or Noise in the hand \
        selection decision making
        in_RD (float): Non-Paretic Arm Bias/Hand Dominance (currently not used)
        trials (int): Number of trials to simulate
        in_showTrial1 (int): Trial onset to play animation fo simulation
        in_showTrial2 (int): 2nd Trial onset to play animation fo simulation
        simulateStroke (bool): True = Trials of treatment
        simulateRehab (bool): True = Trials of treatment
        simulateFU (bool): True = Trials of follow-up (without treatment)
        FORCED_TRIAL (float): normalized value indicating probability of \
        forcing the use of the paretic limb at each trial
        GAIN (float): normalized value indicating ratio of extent \
        amplification of the paretic limb movement.
        STEER (float): normalized value indicating ratio of directional error \
        reduction of the paretic limb movement.

    """

    energies = [0, 0]
    sensitivityUpdateRight = []
    sensitivityUpdateLeft = []
    N = 500
    N_extent = 20
    Nchoice = 10
    leftCortex_extent = [
        Net(math.radians(i * float(360.00 / N_extent)), "left")
        for i in range(N_extent)
    ]
    rightCortex_extent = [
        Net(math.radians(i * float(360.00 / N_extent)), "right")
        for i in range(N_extent)
    ]

    # Update model state
    leftCortex, rightCortex, choiceLeft, choiceRight = updateModelParams(
        Nchoice, simulateStroke, simulateRehab, simulateFU, N, N_extent,
        leftCortex_extent, rightCortex_extent)

    spatialRangeLeft = (90, 270)  # define angles workspace of left arm
    spatialRangeRight = (270, 90)  # define angles workspace of right arm

    # Init action choice nets for storing and updating
    # action-related expected reward values
    rightArm = ArmRewardClass("right", 0, spatialRangeRight)
    leftArm = ArmRewardClass("left", 0, spatialRangeLeft)

    # Init all vars that will be stored in JSONs after simulations
    probability_right = []
    probability_left = []
    listOfAngles = []
    rt = []
    angle_per_trial = []
    choosen_per_trial = []
    errorLeft_extent = []
    errorRight_extent = []
    errorLeft_angle = []
    errorRight_angle = []
    expected_L = []
    expected_R = []
    energy_L = []
    energy_R = []
    actualReward_logs = []

    # Init action choice nets
    weightListCheckLeft = []
    weightListCheckRight = []

    nInput = 250  # Number of possible angles in range 0 to 360
    possibleAngles = np.linspace(0.0, 360.0, nInput)

    # Shuffle PissibleAnles
    np.random.shuffle(possibleAngles)

    for e in range(trials):

        UI.progressbar["maximum"] = trials
        UI.progressbar["value"] = e
        UI.style.configure(
            'text.Horizontal.TProgressbar',
            text='{:g}'.format(e))  # update label
        UI.progressbar.update()
        newdAngle = math.radians(possibleAngles[e % nInput])

        if ((e % nInput) == 0):
            for x in range(nInput):
                auxShuffle = int(np.random.uniform(0, nInput))
                auxShuffle_2 = possibleAngles[auxShuffle]
                possibleAngles[auxShuffle] = possibleAngles[x]
                possibleAngles[x] = auxShuffle_2

        # Vector to target
        newExtentR= np.linalg.norm((-0.2+np.cos(newdAngle))+ 1j * np.sin(newdAngle))
        newExtentL= np.linalg.norm((0.2+np.cos(newdAngle)) + 1j * np.sin(newdAngle))

        # NewExtentLeft is the actual extent of the optimal movement for
        # the right hand/left cortex
        if (simulateRehab):
            # keep applying gain
            newExtentL -= newExtentL * GAIN

        startTime = int(round(time.time() * 1000))
        choosenHand = -1
        handSelected = -1
        acL = 0
        acR = 0
        pacL = 0
        pacR = 0
        ac = 0

        # Left cortex -> right hand direction (Notice that we reverse it here)
        directionLeft, directionRight, errorL, errorR, dvL, dvR = \
            fDirectionCoding(leftCortex, rightCortex, newdAngle)

        extentLeft, extentRight, errorLeft_e, errorRight_e = extentCodingFunc(
            leftCortex_extent, rightCortex_extent, newExtentL, newExtentR,
            newdAngle)

        while (choosenHand == -1):
            currT = int(round(time.time() * 1000))

            [energies, angleShoulder,
             angleElbow] = calculateEnergies.fComputeEnergies(
                 np.vstack((dvL, dvR)) / 3., newdAngle)

            # Old method foe hand selection reported in Han et al. 2008
            # We do not use it for hand selection anymore but only to
            # obtain expected reward scores:
            [expRewardL, expRewardR, p_left, p_right] = returnHandChoice(
                newdAngle, choiceLeft, choiceRight, leftArm, rightArm,
                directionLeft, directionRight, 0, Exploration_Level)
            direc_errorR = getDiffAngle(newdAngle, directionRight)
            direc_errorL = getDiffAngle(newdAngle, directionLeft)

            # Show 5 consecutive trials
            if (e >= in_showTrial1
                    and e < in_showTrial1 + 6) or (e >= in_showTrial2
                                                   and e < in_showTrial2 + 6):
                ac, pacR, pacL = UI.play_trial(
                    angleShoulder[choosenHand], angleElbow[choosenHand],
                    np.cos(newdAngle) /
                    (np.sqrt(np.cos(newdAngle)**2 + np.sin(newdAngle)**2)) /
                    3.,
                    np.sin(newdAngle) /
                    (np.sqrt(np.cos(newdAngle)**2 + np.sin(newdAngle)**2)) / 3.
                    + 0.4, choosenHand, acR, acL, pacR, pacL, ac, expRewardR,
                    expRewardL, startTime, currT, e, False)

            # New method to select arm based on interactive race model
            [choosenHand, acL, acR] = CompetingAccumulators(
                acL, acR, energies, expRewardL, expRewardR)

        rt.append(currT - startTime)
        choosen_per_trial.append(choosenHand)
        angle_per_trial.append(newdAngle)
        errorLeft_extent.append(errorLeft_e)
        errorRight_extent.append(errorRight_e)
        errorLeft_angle.append(direc_errorL)
        errorRight_angle.append(direc_errorR)
        expected_L.append(expRewardL)
        expected_R.append(expRewardR)
        energy_L.append(energies[0])
        energy_R.append(energies[1])

        if (simulateRehab):
            STEER_help = STEER
            directionRight = directionRight + (direc_errorR * STEER_help)

            if (directionRight >= (2*np.pi)):
                directionRight = directionRight - (2*np.pi)
            else:
                if (directionRight < 0):
                    directionRight = directionRight + (2*np.pi)

            if (np.random.uniform(0, 1) < FORCED_TRIAL):
                choosenHand = 1

        if (e >= in_showTrial1
                and e < in_showTrial1 + 6) or (e >= in_showTrial2
                                               and e < in_showTrial2 + 6):
            for step in range(len(angleShoulder)):
                ac, pacR, pacL = UI.play_trial(
                    angleShoulder[step, choosenHand],
                    angleElbow[step, choosenHand],
                    np.cos(newdAngle) /
                    (np.sqrt(np.cos(newdAngle)**2 + np.sin(newdAngle)**2)) /
                    3.,
                    np.sin(newdAngle) /
                    (np.sqrt(np.cos(newdAngle)**2 + np.sin(newdAngle)**2)) / 3.
                    + 0.4, choosenHand, acR, acL, pacR, pacL, ac, expRewardR,
                    expRewardL, startTime, currT, e, True)

        if (e == trials - 1):
            for p in range(len(choiceLeft)):
                weightListCheckLeft.append(choiceLeft[p].weight)
                weightListCheckRight.append(choiceRight[p].weight)

        if (choosenHand == 1):
            actualReward = math.exp(-((direc_errorR**2) / 0.2**2)) - (math.sqrt(errorRight_e**2) * 0.1)
        else:
            actualReward = math.exp(-((direc_errorL**2) / 0.2**2)) - (math.sqrt(errorLeft_e**2) * 0.1)

        actualReward_logs.append(actualReward)

        predictionErrorL = actualReward - expRewardL
        predictionErrorR = actualReward - expRewardR

        # Apply learning rule (RB) without crossed lateralization
        if (choosenHand == 1):
            # cortex left
            for i in range(len(choiceRight)):
                choiceRight[i].weight += ReinforcementBasedLearning * \
                    predictionErrorR * math.exp(
                        -(getDiffAngle(newdAngle, choiceRight[i].center)**2 / (np.pi / 10)**2))

        if (choosenHand == 0):
            # cortex right
            for i in range(len(choiceRight)):
                choiceLeft[i].weight += ReinforcementBasedLearning * \
                    predictionErrorL * math.exp(
                        -(getDiffAngle(newdAngle, choiceLeft[i].center)**2 / (np.pi / 10)**2))

        # Store trial state and apply learning rule to improve extent conding
        # with crossed lateralization
        if (choosenHand == 1):
            sensitivityUpdateLeft = []
            sumOfSquareActivitiesLeft = 0
            for i in range(len(leftCortex)):
                sumOfSquareActivitiesLeft += leftCortex[i].activity
                sensitivityUpdateLeft.append(math.degrees(leftCortex[i].learningRuleFunc(directionRight, newdAngle, ErrorBasedLearning, UseDependentLearning)))
            for i in range(len(leftCortex_extent)):
                leftCortex_extent[i].learningRuleFunc_extent(errorLeft_e)

        if (choosenHand == 0):
            sensitivityUpdateRight = []
            sumOfSquareActivitiesRight = 0
            for i in range(len(rightCortex)):
                sumOfSquareActivitiesRight += rightCortex[i].activity
                sensitivityUpdateRight.append(math.degrees(rightCortex[i].learningRuleFunc(directionLeft, newdAngle, ErrorBasedLearning, UseDependentLearning)))
            for i in range(len(rightCortex_extent)):
                rightCortex_extent[i].learningRuleFunc_extent(errorRight_e)

    # Update progress bar
    UI.style.configure(
        'text.Horizontal.TProgressbar',
        text='{:g}'.format(trials))  # update label trial
    UI.progressbar["value"] = trials
    UI.progressbar.update()

    # Collect data of model current state
    p_right = 0
    p_left = 0
    probability_right = []
    probability_left = []
    error_right = []
    error_left = []
    error_extent_right = []
    error_extent_left = []
    error = []
    weight_extent_Left = []
    weight_extent_Right = []
    expectedRewardR = []
    expectedRewardL = []
    energy_L = []
    energy_R = []
    possibleAngles = np.arange(0, 360, 360 / 500.)

    for i in range(len(possibleAngles)):
        angle = math.radians(possibleAngles[i])
        a = [(-0.2 + math.cos(angle)), (math.sin(angle))]
        newExtentR = np.linalg.norm(a)
        b = [(0.2 + math.cos(angle)), (math.sin(angle))]
        newExtentL = np.linalg.norm(b)
        [directionLeft, directionRight, errorL, errorR, dvL, dvR] = \
            fDirectionCoding(leftCortex, rightCortex, angle)
        [expRewardL, expRewardR, p_left, p_right] = returnHandChoice(
            angle, choiceLeft, choiceRight, leftArm, rightArm, directionLeft,
            directionRight, 0, Exploration_Level)
        probability_right.append(p_right)
        probability_left.append(p_left)
        error_right.append(errorR)
        error_left.append(errorL)
        expectedRewardL.append(expRewardL)
        expectedRewardR.append(expRewardR)
        extentLeft, extentRight, errorLeft_e, errorRight_e = extentCodingFunc(
            leftCortex_extent, rightCortex_extent, newExtentL, newExtentR,
            newdAngle)
        error_extent_right.append(errorRight_e)
        error_extent_left.append(errorLeft_e)
        if (p_right > p_left):
            error.append(errorR)
        else:
            error.append(errorL)
        [energies, angleShoulder,
         angleElbow] = calculateEnergies.fComputeEnergies(
             np.vstack((dvL, dvR)) / 3., angle)
        energy_L.append(energies[0])
        energy_R.append(energies[1])

    sensitivityLeft = []
    sensitivityRight = []
    for j in range(len(rightCortex)):
        sensitivityRight.append(math.degrees(rightCortex[j].sensitivity))
    for j in range(len(leftCortex)):
        sensitivityLeft.append(math.degrees(leftCortex[j].sensitivity))
    for j in range(N_extent):
        weight_extent_Left.append(leftCortex_extent[j].weight)
        weight_extent_Right.append(rightCortex_extent[j].weight)

    # Show plots of current model state
    UI.drawTrialData(e, rt, angle_per_trial, possibleAngles, probability_left, probability_right, errorLeft_angle, errorRight_angle, errorLeft_extent, errorRight_extent, expectedRewardL, expectedRewardR, energy_L, energy_R, sensitivityLeft, sensitivityRight, choosen_per_trial)

    # Save JSON files with current model state for future recovery or analysis
    meanProbLeft = []
    meanProbRight = []
    dictWeights = {
        'weightListCheckLeft': weightListCheckLeft,
        'weightListCheckRight': weightListCheckRight,
        'sensitivityUpdateLeft': sensitivityLeft,
        'sensitivityUpdateRight': sensitivityRight,
        'weight_extent_R': weight_extent_Right,
        'weight_extent_L': weight_extent_Left,
        "error_extent_right": error_extent_right,
        "error_extent_left": error_extent_left,
        "error_right": error_right,
        "error_left": error_left
    }

    if (simulateStroke or simulateRehab):
        with open('Trainned_model_stroke.json', 'w') as f:
            # save training weights to file
            json.dump(dictWeights, f)
    else:
        if (simulateFU):
            with open('Trainned_model_rehab.json', 'w') as f:
                # save training weights to file
                json.dump(dictWeights, f)
        else:
            with open('Trainned_model.json', 'w') as f:
                # save training weights to file
                json.dump(dictWeights, f)

    dictWeights = {
        'meanProbRight': probability_right,
        'meanProbLeft': probability_left,
        'listOfAngles': listOfAngles
    }
    with open('Trainned_probabilities.json', 'w') as file:
        # save training weights to file
        json.dump(dictWeights, file)

    dictLogs = {
        'Chosen': choosen_per_trial,
        'angle_per_trial': angle_per_trial,
        'rt': rt,
        'errorLeft_extent': errorLeft_extent,
        'errorRight_extent': errorRight_extent,
        'errorLeft_angle': errorLeft_angle,
        'errorRight_angle': errorRight_angle,
        'expected_L': expected_L,
        'expected_R': expected_R,
        'energy_L': energy_L,
        'energy_R': energy_R,
        'actualReward_logs': actualReward_logs
    }
    with open('Trainned_logs.json', 'w') as file:
        # save training weights to file
        json.dump(dictLogs, file)

    print("JSON files saved")


def updateModelParams(Nchoice, simulateStroke, simulateRehab, simulateFU, N,
                      N_extent, leftCortex_extent, rightCortex_extent):

    # Load JSON Files to recover current state of the model according to phase
    if (simulateStroke):
        f = json.loads(open('Trainned_model.json').read())
        leftCortex = [
            Net(math.radians(f['sensitivityUpdateLeft'][i]), "left")
            for i in range(len(f['sensitivityUpdateLeft']))
        ]
        rightCortex = [
            Net(math.radians(f['sensitivityUpdateRight'][i]), "right")
            for i in range(len(f['sensitivityUpdateRight']))
        ]

        for i in range(N_extent):
            leftCortex_extent[i].weight = (
                f['weight_extent_L'][i])  # update activity of each cell
            rightCortex_extent[i].weight = (
                f['weight_extent_R'][i])  # update activity of each cell

        # Simulating stroke: we remove  50% of neurons in left cortex
        # Notice a decrease in performance of the right hand
        listOfDeadNeurons = []
        listOfDeadNeurons2 = []

        for i in range(len(leftCortex)):
            if ((leftCortex[i].sensitivity < math.radians(90))):
                listOfDeadNeurons.append(i)

        for i in range(len(listOfDeadNeurons)):
            neuron = listOfDeadNeurons[i] - i
            # Simulate a stroke
            del leftCortex[neuron]

        choiceLeft = [
            ActionChoiceClass("left", (i * 2*np.pi / Nchoice),
                              f['weightListCheckLeft'][i], 0)
            for i in range(Nchoice)
        ]
        choiceRight = [
            ActionChoiceClass("right", (i * 2*np.pi / Nchoice),
                              f['weightListCheckRight'][i], 0)
            for i in range(Nchoice)
        ]

    else:

        if (simulateRehab or simulateFU):

            f = json.loads(open('Trainned_model_stroke.json').read())
            leftCortex = [
                Net(math.radians(f['sensitivityUpdateLeft'][i]), "left")
                for i in range(len(f['sensitivityUpdateLeft']))
            ]
            rightCortex = [
                Net(math.radians(f['sensitivityUpdateRight'][i]), "right")
                for i in range(len(f['sensitivityUpdateRight']))
            ]

            for i in range(N_extent):
                leftCortex_extent[i].weight = (
                    f['weight_extent_L'][i])  # update activity of each cell
                rightCortex_extent[i].weight = (
                    f['weight_extent_R'][i])  # update activity of each cell

            choiceLeft = [
                ActionChoiceClass("left", (i * 2*np.pi / Nchoice),
                                  f['weightListCheckLeft'][i], 0)
                for i in range(Nchoice)
            ]
            choiceRight = [
                ActionChoiceClass("right", (i * 2*np.pi / Nchoice),
                                  f['weightListCheckRight'][i], 0)
                for i in range(Nchoice)
            ]

        else:

            leftCortex = [
                Net(math.radians(i * float(360.00 / N)), "left")
                for i in range(N)
            ]
            rightCortex = [
                Net(math.radians(i * float(360.00 / N)), "right")
                for i in range(N)
            ]

            for i in range(N_extent):
                leftCortex_extent[
                    i].weight = 0.3  # set baseline activity of each cell
                rightCortex_extent[
                    i].weight = 0.3  # set baseline activity of each cell

            # Weights should be initialized to...
            choiceLeft = [
                ActionChoiceClass("left", (i * 2*np.pi / Nchoice), 0.5, 0)
                for i in range(Nchoice)
            ]
            choiceRight = [
                ActionChoiceClass("right", (i * 2*np.pi / Nchoice), 0.5, 0)
                for i in range(Nchoice)
            ]

    return leftCortex, rightCortex, choiceLeft, choiceRight
