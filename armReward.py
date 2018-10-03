#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com

# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#

import math
import random
import numpy as np


class ArmRewardClass:
    def __init__(self, cortex, actionValue, prefWorkSpace):
        self.cortex = cortex
        self.actionValue = actionValue
        self.prefWorkSpace = prefWorkSpace
