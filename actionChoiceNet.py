#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com
# SPECS Lab. Institute for Bioengineering of Catalunya


# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#

import math
import random
import numpy as np


class ActionChoiceClass:
    def __init__(self, cortex, center, weight, activity):
        self.cortex = cortex
        self.center = center
        self.weight = weight
        self.activity = activity
