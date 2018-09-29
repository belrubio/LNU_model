import math
import random
import numpy as np


class ActionChoiceClass:
    def __init__(self, cortex, center, weight, activity):
        self.cortex = cortex
        self.center = center
        self.weight = weight
        self.activity = activity
