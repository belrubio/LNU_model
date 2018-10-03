#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com
# SPECS Lab. Institute of Bioengineering of Catalunya
#
# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#

from runSimulations import *


def fDirectionCoding(leftCortex, rightCortex, angleTarget):

    """ Computes the population vector and extent according to:
    in Georgopoulos, A. P., Schwartz, A. B., & Kettner, R. E. (1986). Neuronal population coding of movement direction. Science, 233(4771), 1416-1419.

    It also error between the planned and the ideal trajectory.

    Parameters:
        leftCortex (CortexNet): set of neurons of class Net in leftCortex
        rightCortex (CortexNet): set of neurons of class Net in rightCortex
        angleTarget (float): target direction angle

    Returns:
        directionRight: direction of right arm's planned trajectory
        directionLeft: direction of left arm's planned trajectory
        errorRight: right arm's directional error to target
        errorLeft: left arm's directional error to target
        tangSumLeft: sum the tangents of all the angles Left Cortex
        tangSumRight: sum the tangents of all the angles Right Cortex

    """

    # sum the tangentes of all the angles by cortex:
    tangSumLeft = [0, 0]
    tangSumRight = [0, 0]

    # sum the tan of all the angles Left Cortex
    for i in range(len(leftCortex)):
        # update activity of each cell
        leftCortex[i].activationRuleFunc(angleTarget)
        a, x, y = leftCortex[i].getVector()
        tangSumLeft[0] += x
        tangSumLeft[1] += y

    directionLeft = math.atan2(tangSumLeft[1], tangSumLeft[0])
    if (directionLeft < 0):
        directionLeft += (2 * math.pi)
    if (directionLeft >= (2 * math.pi)):
        directionLeft -= (2 * math.pi)

    for i in range(len(rightCortex)):
        # update activity of each cell
        rightCortex[i].activationRuleFunc(angleTarget)
        a, x, y = rightCortex[i].getVector()
        tangSumRight[0] += x
        tangSumRight[1] += y

    directionRight = math.atan2(tangSumRight[1], tangSumRight[0])

    if (directionRight < 0):
        directionRight += (2 * math.pi)
    if (directionRight >= (2 * math.pi)):
        directionRight -= (2 * math.pi)

    # Compute errors and direction vectors
    # for the Right cortex
    errorRight = (min(
        angleTarget - directionRight,
        angleTarget - directionRight + 2 * math.pi,
        angleTarget - directionRight - 2 * math.pi,
        key=abs))**2
    # for the Left cortex
    errorLeft = (min(
        angleTarget - directionLeft,
        angleTarget - directionLeft + 2 * math.pi,
        angleTarget - directionLeft - 2 * math.pi,
        key=abs))**2
    tangSumLeft = tangSumLeft / (
        np.sqrt(tangSumLeft[0]**2 + tangSumLeft[1]**2))
    tangSumRight = tangSumRight / (
        np.sqrt(tangSumRight[0]**2 + tangSumRight[1]**2))

    return directionRight, directionLeft, errorRight, errorLeft, \
        tangSumRight,  tangSumLeft


def extentCodingFunc(leftCortex_extent, rightCortex_extent, newExtentL,
                     newExtentR, angleTarget):
    """ Compute each arm's executed movement extent and extracts error

    Parameters:
        leftCortex_extent: planned right arm movement trajetory extent
        rightCortex_extent: planned left arm movement trajetory extent
        newExtentL: ideal right arm movement trajetory extent to target
        newExtentR: ideal left arm movement trajetory extent to target
        angleTarget: target direction

    Returns:
        extentRight: executed extent of left arm movement
        extentLeft: executed extent of right arm movement
        errorRight_e: left arm movement error in terms of extent
        errorLeft_e: right arm movement error in terms of extent
    """

    # sum the tan by cortex (Georgeopolous, et al. 1986):
    tangSumRight = 0
    tangSumLeft = 0

    for i in range(len(leftCortex_extent)):
        # update activity of each cell
        leftCortex_extent[i].activationExtentRule_Func(angleTarget)

        a = leftCortex_extent[i].getExtent()
        tangSumLeft += a

    extentLeft = tangSumLeft

    for i in range(len(rightCortex_extent)):
        # update activity of each cell
        rightCortex_extent[i].activationExtentRule_Func(angleTarget)
        a = rightCortex_extent[i].getExtent()
        tangSumRight += a

    extentRight = tangSumRight

    errorRight_e = newExtentR - extentRight
    errorLeft_e = newExtentL - extentLeft

    return extentRight, extentLeft, errorRight_e, errorLeft_e
