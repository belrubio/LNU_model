#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# Diogo Santos Pata
# diogo.santos.pata@gmail.com
# SPECS Lab. Institute of Bioengineering of Catalunya
#
# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#

import math
import random
import numpy as np


class Net:

    """
    A class used to represent a pool of motor cortex neurons.

    ...

    Attributes
    ----------
    sensitivity : float
        angle to which this cell has max sensitivity/response
    cortex : net
        the neural net corresponding to each cortex
    activity : float
        the activity of this cell, defined by a truncated cosine function

    Methods
    -------
    getVector()
        Returns coordinates corresponding to the angle

    getExtent()
        Returns extent of the movement

    activationExtentRule_Func()
        Updates self.activity according to distance to target orientation

    activationRuleFunc()
        Updates self.activity according to distance to target orientation

    learningRuleFunc()
        Simulates neural adaptation by updating the self.sensitivity

    learningRuleFunc_extent()
        Simulates neural adaptation by updating the self.weight

    """

    def __init__(self, sensitivity, cortex):
        self.sensitivity = sensitivity
        self.cortex = cortex
        self.activity = 0.0
        self.weight = 0.5
        self.vector = 0

    def getVector(self):
        sensitivity = self.sensitivity
        self.vx = self.activity * math.cos(sensitivity)
        self.vy = self.activity * math.sin(sensitivity)
        self.vector = (self.activity * math.cos(sensitivity), self.activity * math.sin(sensitivity))
        return self.vector, self.vx, self.vy

    def getExtent(self):
        return np.linalg.norm(self.vector)

    def activationExtentRule_Func(self, targetextent):
        self.activity = self.weight * (math.cos(
            min(targetextent - self.sensitivity,
                targetextent - self.sensitivity + 2 * math.pi,
                targetextent - self.sensitivity - 2 * math.pi,
                key=abs)))
        if (self.activity > 0.0):
            self.activity = self.activity
        else:
            self.activity = 0.0

    def activationRuleFunc(self, dAngle):
        act = math.cos(
            min(dAngle - self.sensitivity,
                dAngle - self.sensitivity + 2 * math.pi,
                dAngle - self.sensitivity - 2 * math.pi,
                key=abs))

        k = random.normalvariate(0, (0.15 * act))  # Add noise
        act = act + k

        if (act < 0):
            act = 0

        self.activity = act

    def learningRuleFunc(self, direction, dAngle, supervisedRation,
                         unsupervisedRation):
        smallerAngle2 = min(
            dAngle - self.sensitivity,
            dAngle - self.sensitivity + 2 * math.pi,
            dAngle - self.sensitivity - 2 * math.pi,
            key=abs)

        smallerAngle3 = min(
            dAngle - direction,
            dAngle - direction + 2 * math.pi,
            dAngle - direction - 2 * math.pi,
            key=abs)

        self.sensitivity += (
            supervisedRation * smallerAngle3 * self.activity) + (
                unsupervisedRation * smallerAngle2 * self.activity)

        if (self.sensitivity < 0):
            self.sensitivity = self.sensitivity + (2 * math.pi)
        else:
            if (self.sensitivity >= (2 * math.pi)):
                self.sensitivity = self.sensitivity - (2 * math.pi)

        return self.sensitivity

    def learningRuleFunc_extent(self, error):
            weightLearning = 0.4
            self.weight += (weightLearning * error * self.activity)
