#!/usr/bin/python

from motorCortexNet import *
from actionChoiceNet import *
from SimulationsMain import *

nChoice = 10


def returnHandChoice(dAngle, choiceLeft, choiceRight, leftArm, rightArm,
                     directionRight, directionLeft, trial, Exploration_Level):

    expectedRewardLeft = 0
    for i in range(len(choiceLeft)):
        phi = math.exp(-(((
            min(dAngle - choiceLeft[i].center,
                dAngle - choiceLeft[i].center + 2 * math.pi,
                dAngle - choiceLeft[i].center - 2 * math.pi,
                key=abs)**2)) / ((math.pi / 10)**2)))
        expectedRewardLeft += (choiceLeft[i].weight * phi)

    expectedRewardRight = 0
    for i in range(len(choiceRight)):
        phi = math.exp(-(((
            min(dAngle - choiceRight[i].center,
                dAngle - choiceRight[i].center + 2 * math.pi,
                dAngle - choiceRight[i].center - 2 * math.pi,
                key=abs)**2)) / ((math.pi / 10)**2)))
        expectedRewardRight += (choiceRight[i].weight * phi)

    probabilityOfActionLeft = 1 / (1 + (math.exp(
        -Exploration_Level * (expectedRewardLeft - expectedRewardRight))))
    probabilityOfActionRight = 1 / (1 + (math.exp(
        -Exploration_Level * (expectedRewardRight - expectedRewardLeft))))

    goodLuck = float(random.uniform(0, 1))

    if (goodLuck < probabilityOfActionLeft):
        choosenHand = 0
    else:
        choosenHand = 1

    lateralization_nonUsed = 0.2
    lateralization = 0.0

    if (choosenHand == 1):  # RIGHT WORKSPACE

        prefWorkSpace = rightArm.prefWorkSpace
        direction = directionLeft
        direction2 = directionRight

        if ((0 <= math.degrees(dAngle))
                and (math.degrees(dAngle) <= prefWorkSpace[1])):
            lateralization_nonUsed = 0.0
            lateralization = 0.2
        else:
            if ((prefWorkSpace[0] <= math.degrees(dAngle))
                    and (math.degrees(dAngle) <= 360)):
                lateralization_nonUsed = 0.0
                lateralization = 0.2

    else:  # LEFT WORKSPACE
        prefWorkSpace = leftArm.prefWorkSpace
        direction = directionRight
        direction2 = directionLeft

        # print "left prefWorkSpace ", prefWorkSpace[0], " ", prefWorkSpace[1]
        if ((prefWorkSpace[0] <= math.degrees(dAngle))
                and (math.degrees(dAngle) <= prefWorkSpace[1])):
            lateralization_nonUsed = 0.0
            lateralization = 0.2

    actualReward = math.exp(-((
        min(dAngle - direction,
            dAngle - direction + 2 * math.pi,
            dAngle - direction - 2 * math.pi,
            key=abs)**2) / 0.2**2))

    actualReward_nonUsed = math.exp(-((
        min(dAngle - direction2,
            dAngle - direction2 + 2 * math.pi,
            dAngle - direction2 - 2 * math.pi,
            key=abs)**2) / 0.2**2)) + lateralization_nonUsed

    return choosenHand, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, probabilityOfActionLeft, probabilityOfActionRight, directionLeft


def CompetingAccumulators(accumulatorLeft, accumulatorRight, energies,
                          expectedRewardLeft, expectedRewardRight):

    a = 0.4  # max expected reward is ~1.2 and min is ~0.3
    b = 7  # max energies is around ~0.02 and min is ~0.002
    c = 0.7
    HandSelected = -1
    time.sleep(0.0001)

    # We add noise needed for exploration
    noise = float(random.normalvariate(0, 0.15))
    accumulatorLeft_temp = accumulatorLeft + (
        a * (expectedRewardLeft) - b *
        (energies[0])) + noise  # energy 0 corresponds to left arm
    noise = float(random.normalvariate(0, 0.15))
    accumulatorRight_temp = accumulatorRight + (a * (expectedRewardRight) - b *
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
