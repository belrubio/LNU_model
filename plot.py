#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com
# Diogo Santos Pata
# diogo.santos.pata@gmail.com
# SPECS Lab. Institute for Bioengineering of Catalunya
#
# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#

from __future__ import division
import pygame
import numpy as np
import time
import calculateEnergies

global targetPos, energLevelRight, energLevelLeft, leftArmAngle, leftForeArmAngle, rightArmAngle, rightForeArmAngle

foreArmLenght = 220 / 2
armLenght = 250 / 2
targetPos = [200, 400]
energLevelLeft = 490
energLevelRight = 490
energy = [0, 0]
size = [800, 600]


# Play animation of each trial simulation of the decision making and execution
def gui(
        armAngleG=0,
        foreArmAngleG=0,
        targetXG=0,  # X location of target
        targetYG=0,  # Y location of target
        selectedHand=-1,
        acL=0,  # accumulator list of values Right
        acR=0,  # accumulator list of values Left
        acLprev=0,  # previous accumulator value Right
        acRprev=0,  # previous accumulator value Left
        ac=0,
        expR_L=0,  # Expected Value for Right Hand
        expR_R=0,  # Expected Value for Left Hand
        startTime=0,  # Trial time onset
        currentT=0):  # Current Time stamp

    rt = currentT - startTime
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("TRIAL SIMULATION")
    done = False
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('helvetica', 18)
    rightShoulderPos = [340, 300]
    rightArmAngle = -19.8
    rightForeArmAngle = -132.4 + rightArmAngle
    leftShoulderPos = [260, 300]
    leftArmAngle = -160
    leftForeArmAngle = 132.4 + leftArmAngle
    energy = calculateEnergies.getEnergy()

    if selectedHand == 1:
        rightArmAngle = armAngleG
        rightForeArmAngle = armAngleG + foreArmAngleG
        acR = acRprev
        acL = acLprev
    else:
        if selectedHand == 0:
            leftArmAngle = -armAngleG
            leftForeArmAngle = -armAngleG - foreArmAngleG
            acR = acRprev
            acL = acLprev
        else:
            ac = np.vstack((ac, 0))
            acR = np.hstack((acRprev, acR))
            acL = np.hstack((acLprev, acL))

    targetPos = [290 + targetXG * 250,
                 290 - targetYG * 250]
    screen.fill(pygame.Color(245, 250, 255))
    textEnerg = font.render("Energies", True, (0, 0, 0))
    textReward = font.render("Exp. Reward", True, (0, 0, 0))
    textEnergLeft = font.render("Left", True, (0, 0, 0))
    textEnergRight = font.render("Right", True, (0, 0, 0))
    textWorkspace = font.render("Workspace", True, (0, 0, 0))
    textTime = font.render(str(rt), True, (0, 0, 0))
    textPlus = font.render("+", True, (0, 0, 0))
    textMinus = font.render("-", True, (0, 0, 0))

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            pygame.quit()

    rightElbow = [
        rightShoulderPos[0] + armLenght * np.cos(np.radians(rightArmAngle)),
        rightShoulderPos[1] + armLenght * np.sin(np.radians(rightArmAngle))
    ]
    rightHand = [
        rightElbow[0] + foreArmLenght * np.cos(np.radians(rightForeArmAngle)),
        rightElbow[1] + foreArmLenght * np.sin(np.radians(rightForeArmAngle))
    ]
    leftElbow = [
        leftShoulderPos[0] + armLenght * np.cos(np.radians(leftArmAngle)),
        leftShoulderPos[1] + armLenght * np.sin(np.radians(leftArmAngle))
    ]
    leftHand = [
        leftElbow[0] + foreArmLenght * np.cos(np.radians(leftForeArmAngle)),
        leftElbow[1] + foreArmLenght * np.sin(np.radians(leftForeArmAngle))
    ]

    pygame.draw.rect(screen, (250, 250, 250), [10, 60, 550, 340],
                     0)  # workspace
    pygame.draw.rect(screen, (0, 0, 0), [10, 60, 550, 340], 2)  # workspace
    pygame.draw.rect(screen, (224, 238, 238),
                     [targetPos[0], targetPos[1], 20, 20])  # target
    pygame.draw.rect(screen, (0, 0, 0), [targetPos[0], targetPos[1], 20, 20],
                     2)  # target
    pygame.draw.line(screen, (75, 75, 75), rightShoulderPos, rightElbow,
                     10)  # rightArm
    pygame.draw.line(screen, (75, 75, 75), rightElbow, rightHand,
                     10)  # rightForearm
    pygame.draw.ellipse(
        screen, (200, 10, 10),
        [rightElbow[0] - 10, rightElbow[1] - 10, 20, 20])  # rightElbow
    pygame.draw.ellipse(
        screen, (200, 10, 10),
        [rightShoulderPos[0] - 10, rightShoulderPos[1] - 10, 20, 20
         ])  # rightShoulder

    pygame.draw.line(screen, (75, 75, 75), leftShoulderPos, leftElbow,
                     10)  # leftArm
    pygame.draw.line(screen, (75, 75, 75), leftElbow, leftHand,
                     10)  # leftForearm
    pygame.draw.ellipse(
        screen, (10, 10, 200),
        [leftElbow[0] - 10, leftElbow[1] - 10, 20, 20])  # leftElbow
    pygame.draw.ellipse(
        screen, (10, 10, 200),
        [leftShoulderPos[0] - 10, leftShoulderPos[1] - 10, 20, 20
         ])  # leftShoulder

    # energies
    pygame.draw.rect(screen, (209, 238, 238), [610, 420, 150, 150],
                     0)  # workspace
    pygame.draw.line(screen, (50, 50, 50), [700, 490],
                     [700, energLevelRight-energy[1] * 2000],
                     12)  # energy right
    pygame.draw.line(screen, (50, 50, 50), [650, 490],
                     [650, energLevelLeft-energy[0] * 2000],
                     12)  # energy left
    pygame.draw.polygon(screen, (25, 25, 25),
                        ((670, 180), (690, 180), (690, 190), (700, 190),
                         (680, 210), (660, 190), (670, 190)))
    screen.blit(textMinus, [710, 400])

    # exected reward
    pygame.draw.rect(screen, (209, 238, 238), [610, 30, 150, 150],
                     0)  # workspace
    pygame.draw.line(screen, (50, 50, 50), [700, 120],
                     [700, 120 - expR_R * 25], 12)  # exp reward right
    pygame.draw.line(screen, (50, 50, 50), [650, 120],
                     [650, 120 - expR_L * 25], 12)  # exp reward left
    pygame.draw.polygon(screen, (25, 25, 25),
                        ((670, 420), (690, 420), (690, 410), (700, 410),
                         (680, 390), (660, 410), (670, 410)))
    screen.blit(textPlus, [705, 190])

    # accumulators
    accumulatorsFunc(range(len(ac)), acR, screen, font, [200, 10, 10], 0)
    accumulatorsFunc(range(len(ac)), -acL, screen, font, [10, 10, 200], 100)

    screen.blit(textEnerg, [650, 535])
    screen.blit(textEnergLeft, [640, 510])
    screen.blit(textEnergRight, [680, 510])
    screen.blit(textWorkspace, [250, 420])
    screen.blit(textReward, [630, 150])
    screen.blit(textEnergLeft, [640, 125])
    screen.blit(textEnergRight, [680, 125])
    screen.blit(textTime, [730, 310])

    pygame.display.flip()
    time.sleep(0.01)

    return ac, acL, acR


def accumulatorsFunc(x, y, screen, font, rgb, initY):

    # Display interactive race model activity for decision making (right panel)
    w, h = screen.get_size()
    pygame.draw.line(screen, (100, 100, 100), (0 + 610, 0.5 * -100 + 370),
                     (15 * 7 + 610, 0.5 * -100 + 370), 3)
    y = y * (-100)

    for i in range(len(x) - 1):
        pygame.draw.line(
            screen, rgb, (int(x[i]) * 4 + 610, int(y[i]) + 370 - initY),
            (int(x[i + 1]) * 4 + 610, int(y[i + 1]) + 370 - initY), 2)

    textAccumulator = font.render("Accumulator", True, (0, 0, 0))
    screen.blit(textAccumulator, [630, 230])
    pygame.draw.rect(screen, (0, 0, 0), [590, 210, 190, 190], 2)  # workspace


def close_gui():
    pygame.display.quit()
    pygame.quit()
