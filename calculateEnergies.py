#!/usr/bin/python
# ----------------------------------------------------------------------------
# 2018, Belen Rubio Ballester
# belen.rubio.ballester@gmail.com

# Distributed under the terms of the GNU General Public License (GPL-3.0).
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
#

import numpy as np
import scipy.signal
import time
import _thread

# PhysParams used here were obtained from data in http://www1.i2r.a-star.edu.sg/~kptee/BiolCyb04.pdf
# Centers of mass can be obtained from http://www.exrx.net/Kinesiology/Segments.html

physParams = {
    'inertiaMShoulder': 0.0141,
    'inertiaMElbow': 0.0188,
    'massShoulder': 1.93,
    'massElbow': 1.52,
    'momentShoulderPos': 0.0141,
    'momentElbowPos': 0.0188,
    'upperArm': 0.27241,
    'lowerArm': 0.386786,
    'segmentalCenterOfMass_upperarm': 0.165,
    'segmentalCenterOfMass_forearm': 0.19
}


listBiomechanics = ['T1Major', 'T1Minor']
listStrings = ['RIGHT', 'LEFT']
fs = 10
Nstep = 41
aux = np.ones(Nstep) * np.nan


global Energy
Energy = [0, 0]


def fComputeEnergies(vector, angleTarget):

    '''Compute Energies or Costs associated to each arm's planned movement

    Parameters:
        vector: movement trajectory vector
        angleTarget (float): target direction angle

    Returns:
        energy: cost values associated to each arm's reaching movement
        all_s_angles (in eulers): shoulders angles sequence to be executed
        all_e_angles (in eulers): elbows angles sequence to be executed
    '''

    auxx = np.ones(Nstep) * np.nan
    all_s_angles = np.ones((Nstep, 2)) * np.nan
    all_e_angles = np.ones((Nstep, 2)) * np.nan

    for i in range(Nstep):
        aux[i] = 1 / (1 + np.e**-(i - Nstep / 2))
        auxx[i] = i

    for hand in range(2):

        listaX = vector[hand, 0] * aux
        listaY = 0.4 + ((vector[hand, 1]) * aux)

        [s_angles, e_angles] = fComputeTrajectories(
            listaX, listaY, hand, angleTarget)

        [s_torques, e_torques] = fComputeTorques(s_angles, e_angles)

        Energy[hand] = fComputeEnergy(s_angles, e_angles, s_torques, e_torques)
        all_s_angles[:, hand] = s_angles
        all_e_angles[:, hand] = e_angles

    return Energy, np.degrees(all_s_angles), np.degrees(all_e_angles)


def fComputeEnergy(sa, ea, st, et):
    # Compute derivative of acceleration = jerk
    se_dot3 = np.vstack((sa, ea))
    shifted_se_dot3 = np.roll(se_dot3, 1, 1)
    deltaTheta = shifted_se_dot3 - se_dot3
    deltaTheta[:, 0] = [0., 0.]
    torques_all = np.vstack((st[~np.isnan(st)], et[~np.isnan(et)]))
    return np.sum(np.around(np.absolute(torques_all * deltaTheta), decimals=6))


def fComputeTorques(s_angles, e_angles):
    # Compute derivatives
    S_angleVelocity = np.diff(s_angles, 1, 0)
    S_angleVelocity = np.hstack((S_angleVelocity[0], S_angleVelocity))
    E_angleVelocity = np.diff(e_angles, 1, 0)
    E_angleVelocity = np.hstack((E_angleVelocity[0], E_angleVelocity))

    S_angleAcc = np.diff(S_angleVelocity, 1, 0)
    S_angleAcc = np.hstack((S_angleAcc[0], S_angleAcc))
    E_angleAcc = np.diff(E_angleVelocity, 1, 0)
    E_angleAcc = np.hstack((E_angleAcc[0], E_angleAcc))

    ls = physParams["upperArm"]
    le = physParams["lowerArm"]
    ms = physParams["massShoulder"]
    me = physParams["massElbow"]
    rs = physParams["segmentalCenterOfMass_upperarm"]
    re = physParams["segmentalCenterOfMass_forearm"]
    Is = physParams["momentShoulderPos"]
    Ie = physParams["momentElbowPos"]

    # define terms of function
    alpha = ms * rs**2 + Is + me * (
        ls**2 + re**2 + 2 * ls * re * np.cos(e_angles)) + Ie
    beta = me * ls * re * np.cos(e_angles) + me * re + Ie
    gama = me * ls * re * np.sin(e_angles)

    # we dont have delta because shoulder position is fixed
    epsilon = me * re**2 + Ie
    S_Torques = np.ones(len(e_angles)) * np.nan
    E_Torques = np.ones(len(e_angles)) * np.nan

    # Compute torques according to L.B.BAGESTEIRO
    # AND R.L. SAINBURG J Neurophysiol Vol 88 p.2420
    for s in range(len(e_angles)):
        S_Torques[s] = alpha[s] * S_angleAcc[s] + beta[s] * E_angleAcc[
            s] - gama[s] * E_angleVelocity[s] - 2 * gama[s] * S_angleVelocity[
                s] * E_angleVelocity[s]
        E_Torques[s] = epsilon * E_angleAcc[s] + beta[s] * S_angleAcc[
            s] + gama[s] * (S_angleVelocity[s]**2)

    return S_Torques, E_Torques


def fComputeTrajectories(listaX, listaY, hand, angleTarget):
    # calculate inverse kinematics
    a = 0.48  # length of the forearm
    b = 0.51  # length of the arm
    h = 1
    hdist = 0.2  # distance to the center or the circle in the horizontal axis
    angleElbow = np.ones(Nstep) * np.nan
    angleShoulder = np.ones(Nstep) * np.nan

    if (hand == 0):
        h = -1
        hdist = -0.2  # distance to the center or the circle in the horiz. axis

    # calculate angles for each step in the hand trajectory
    for step in range(len(listaX)):
        [angleShoulder[step], angleElbow[step]] = ikArm(
            listaX[step] - hdist * aux[step], listaY[step], h)

    # 0 index corresponds with right cortex trajectory vector and left hand
    if (hand == 0):
        allAngles = np.vstack((angleShoulder, angleElbow))
    else:
        allAngles = np.vstack((-(angleShoulder), -angleElbow))

    return np.radians(allAngles)


def ikArm(x, y, h):
    a = 0.48
    b = 0.51

    try:
        d = np.sqrt(x * x + y * y)
        k = (d * d - b * b + a * a) / (2 * d)
        m = np.sqrt(a * a - k * k)

    except ValueError:
        print ("Math function error. Probably square root of negative number. \
            No valid joint solution.")
        return

    theta = np.degrees(np.arctan2(float(y), float(x)) - np.arctan2(h * m, k))
    phi = np.degrees(np.arctan2(h * m, k) + np.arctan2(h * m, (d - k)))
    returnAngles = [theta, phi]
    return returnAngles


def getEnergy():
    return Energy
