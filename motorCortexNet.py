#!/usr/bin/python
import math
import random
import numpy as np


class Net:
    def __init__(self, sensitivity, cortex):
        self.sensitivity = sensitivity
        self.cortex = cortex
        self.activity = 0.0
        self.meanactivity = 0.0
        self.activity1 = 0.0
        self.weight = 0.0

    def tangArcFunc(self):
        sensitivity = self.sensitivity

        self.vx = math.cos(sensitivity)
        self.vy = math.sin(sensitivity)
        self.vx = self.activity * self.vx
        self.vy = self.activity * self.vy
        tangArc = (self.activity * self.vx, self.activity * self.vy)
        return tangArc, self.vx, self.vy

    def getExtent(self):
        sensitivity = self.sensitivity

        self.vx = math.cos(sensitivity)
        self.vy = math.sin(sensitivity)
        self.vx = self.activity * self.vx
        self.vy = self.activity * self.vy
        tangArc = (self.activity * self.vx, self.activity * self.vy)
        act = np.linalg.norm(tangArc)
        return act

    def activationExtentRule_Func(self, targetextent):
        activityE = self.weight * (math.cos(
            min(targetextent - self.sensitivity,
                targetextent - self.sensitivity + 2 * math.pi,
                targetextent - self.sensitivity - 2 * math.pi,
                key=abs)))
        if (activityE > 0.0):
            self.activity = activityE
        else:
            self.activity = 0.0
        return self.activity

    def activationRuleFunc(self, dAngle, meanactivity):
        activity1 = math.cos(
            min(dAngle - self.sensitivity,
                dAngle - self.sensitivity + 2 * math.pi,
                dAngle - self.sensitivity - 2 * math.pi,
                key=abs))

        k = random.normalvariate(0, (0.15 * activity1))  # Add noise
        activity = activity1 + k

        if (activity < 0):
            activity = 0

        self.activity = activity

        return activity, k

    def activityFunc(self):
        activity = self.actitivity
        return activity

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
