#!/usr/bin/python
import math
import random
import numpy as np


class ArmRewardClass:
    def __init__(self, cortex, actionValue, prefWorkSpace):
        self.cortex = cortex
        self.actionValue = actionValue
        self.prefWorkSpace = prefWorkSpace
