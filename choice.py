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


from motorCortexNet import *
from actionChoiceNet import *
from runSimulations import *
nChoice = 10


def returnHandChoice(dAngle, choiceLeft, choiceRight, leftArm, rightArm,
                     directionL, directionR, trial, Exploration_Level):
    """

    Method for decision making on hand selection as in:
    Han, C. E., Arbib,  M. A., and Schweighofer, N. (2008).
    Stroke rehabilitation reaches a threshold.
    PLoS computational biology, 4(8), e1000133.

    """

    # Compute expected reward for the Left Arm
    expRewardL = 0
    for i in range(len(choiceLeft)):
        phi = math.exp(-(((
            min(dAngle - choiceLeft[i].center,
                dAngle - choiceLeft[i].center + 2 * math.pi,
                dAngle - choiceLeft[i].center - 2 * math.pi,
                key=abs)**2)) / ((math.pi / 10)**2)))
        expRewardL += (choiceLeft[i].weight * phi)

    # Compute expected reward for the Right Arm
    expRewardR = 0
    for i in range(len(choiceRight)):
        phi = math.exp(-(((
            min(dAngle - choiceRight[i].center,
                dAngle - choiceRight[i].center + 2 * math.pi,
                dAngle - choiceRight[i].center - 2 * math.pi,
                key=abs)**2)) / ((math.pi / 10)**2)))
        expRewardR += (choiceRight[i].weight * phi)

    # Compute probability of selection for each arm
    # according to Han, et al. 2008 - we do not use the lateralization term
    # therefore this estimate does not take into account cost
    pActionLeft = 1 / (1 + (math.exp(-Exploration_Level *
                                     (expRewardL - expRewardR))))
    pActionRight = 1 / (1 + (math.exp(-Exploration_Level *
                                      (expRewardR - expRewardL))))

    # Throw a dice and make a decision
    goodLuck = float(random.uniform(0, 1))
    if (goodLuck < pActionLeft):
        choosenHand = 0
    else:
        choosenHand = 1

    # Define Hand Dominance Bias (constant for the moment)
    # according to target position:
    lateralization_nonUsed = 0.2
    lateralization = 0.0

    # For the right workspace
    if (choosenHand == 1):
        prefWorkSpace = rightArm.prefWorkSpace
        direction = directionR
        direction2 = directionL
        if ((0 <= math.degrees(dAngle))
                and (math.degrees(dAngle) <= prefWorkSpace[1])):
            lateralization_nonUsed = 0.0
            lateralization = 0.2
        else:
            if ((prefWorkSpace[0] <= math.degrees(dAngle))
                    and (math.degrees(dAngle) <= 360)):
                lateralization_nonUsed = 0.0
                lateralization = 0.2

    # For the left workspace
    else:
        prefWorkSpace = leftArm.prefWorkSpace
        direction = directionL
        direction2 = directionR
        if ((prefWorkSpace[0] <= math.degrees(dAngle))
                and (math.degrees(dAngle) <= prefWorkSpace[1])):
            lateralization_nonUsed = 0.0
            lateralization = 0.2

    # Compute actual rewards depending of the directional error
    # as described in Han, et al. 2008, however our estimate does not
    # require a penalization for contralateral movements as in Han 2008
    actualReward = math.exp(-((
        min(dAngle - direction,
            dAngle - direction + 2 * math.pi,
            dAngle - direction - 2 * math.pi,
            key=abs)**2) / 0.2**2))

    actualReward_nonUsed = math.exp(-((
        min(dAngle - direction2,
            dAngle - direction2 + 2 * math.pi,
            dAngle - direction2 - 2 * math.pi,
            key=abs)**2) / 0.2**2))  # + lateralization_nonUsed

    return expRewardL, expRewardR, pActionLeft, pActionRight


def CompetingAccumulators(accumulatorLeft, accumulatorRight, energies,
                          expRewardL, expRewardR):
    """
    Ballester, B. R., Maier, M., Mozo, R. M. S. S., Castañeda, V., Duff, A.,
    & Verschure, P. F. (2016).
    Counteracting learned non-use in chronic stroke patients with
    reinforcement-induced movement therapy. Journal of neuroengineering
    and rehabilitation, 13(1), 74.
    """

    a = 0.4  # weight of expected reward for decision (not normalized)
    b = 10  # weight of cost for decision (not normalized)
    c = 0.7  # weight of competing action for decision (not normalized)
    HandSelected = -1
    time.sleep(0.0001)  # for RTs debug temp

    # We add noise needed for exploration
    noise = float(random.normalvariate(0, 0.15))
    accumulatorLeft_temp = accumulatorLeft + (
        a * (expRewardL) - b *
        (energies[0])) + noise  # energy 0 corresponds to left arm
    noise = float(random.normalvariate(0, 0.15))
    accumulatorRight_temp = accumulatorRight + (a * (expRewardR) - b *
                                                (energies[1])) + noise

    accumulatorLeft = accumulatorLeft_temp - c * accumulatorRight_temp
    accumulatorRight = accumulatorRight_temp - c * accumulatorLeft_temp

    if (accumulatorLeft < 0):
        accumulatorLeft = 0
    if (accumulatorRight < 0):
        accumulatorRight = 0

    if (accumulatorLeft > 1 or accumulatorRight > 1):
        if (accumulatorRight > accumulatorLeft):
            HandSelected = 1
        else:
            if (accumulatorLeft > accumulatorRight):
                HandSelected = 0

    return HandSelected, accumulatorLeft, accumulatorRight
