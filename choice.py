from motorCortexNet import *
from actionChoiceNet import *
from runSimulations import *
nChoice = 10


def returnHandChoice(dAngle, choiceLeft, choiceRight, leftArm, rightArm,
                     directionR, directionL, trial, Exploration_Level):
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
    # according to Han, et al. 2008
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
        direction = directionL
        direction2 = directionR
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
        direction = directionR
        direction2 = directionL
        if ((prefWorkSpace[0] <= math.degrees(dAngle))
                and (math.degrees(dAngle) <= prefWorkSpace[1])):
            lateralization_nonUsed = 0.0
            lateralization = 0.2

    # Compute actual rewards depending of the directional error
    # as described in Han, et al. 2008
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

    a = 0.4  # max expected reward is ~1.2 and min is ~0.3
    b = 7  # max energies is around ~0.02 and min is ~0.002
    c = 0.7
    HandSelected = -1
    time.sleep(0.0001)

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
