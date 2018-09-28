import numpy as np
import scipy.signal
import time
import _thread

# Centers of mass can be obtained from http://www.exrx.net/Kinesiology/Segments.html
# PhysParams used here were obtained from data in http://www1.i2r.a-star.edu.sg/~kptee/BiolCyb04.pdf
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
Energy = [0, 0]


def getEnergy():
    return Energy


def fComputeEnergies(vector, newdAngle, extentRight, extentLeft):
    global Energy
    auxx = np.ones(Nstep) * np.nan
    all_s_angles = np.ones((Nstep, 2)) * np.nan
    all_e_angles = np.ones((Nstep, 2)) * np.nan

    for i in range(Nstep):
        aux[i] = 1 / (1 + np.e**-(i - Nstep / 2))
        auxx[i] = i

    for hand in range(2):

        listaX = vector[hand, 0] * aux
        listaY = 0.4 + ((vector[hand, 1]) * aux)

        [s_angles, e_angles] = funcionComputeTrajectories(
            listaX, listaY, hand, newdAngle)

        [s_torques, e_torques] = fComputeTorques(s_angles, e_angles)

        Energy[hand] = fComputeEnergy(s_angles, e_angles, s_torques, e_torques)
        all_s_angles[:, hand] = s_angles
        all_e_angles[:, hand] = e_angles

    return Energy, np.degrees(all_s_angles), np.degrees(all_e_angles)


def fComputeEnergy(sa, ea, st, et):
    #Compute derivative of acceleration = jerk
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

    #define terms of function
    alpha = ms * rs**2 + Is + me * (
        ls**2 + re**2 + 2 * ls * re * np.cos(e_angles)) + Ie
    beta = me * ls * re * np.cos(e_angles) + me * re + Ie
    gama = me * ls * re * np.sin(e_angles)

    # we dont have delta because shoulder position is fixed
    epsilon = me * re**2 + Ie
    S_Torques = np.ones(len(e_angles)) * np.nan
    E_Torques = np.ones(len(e_angles)) * np.nan

    #Compute torques following paper from L.B.BAGESTEIRO AND R.L. SAINBURG J Neurophysiol Vol 88 p.2420
    for s in range(len(e_angles)):
        S_Torques[s] = alpha[s] * S_angleAcc[s] + beta[s] * E_angleAcc[
            s] - gama[s] * E_angleVelocity[s] - 2 * gama[s] * S_angleVelocity[
                s] * E_angleVelocity[s]
        E_Torques[s] = epsilon * E_angleAcc[s] + beta[s] * S_angleAcc[
            s] + gama[s] * (S_angleVelocity[s]**2)

    return S_Torques, E_Torques


def funcionComputeTrajectories(listaX, listaY, hand, newdAngle):

    #% calculate inverse kinematics
    a = 0.48
    b = 0.51
    h = 1
    hdist = 0.2
    angleElbow = np.ones(Nstep) * np.nan
    angleShoulder = np.ones(Nstep) * np.nan

    if (hand == 0):
        h = -1
        hdist = -0.2

    #calculate angles for each step in the hand trajectory
    for step in range(len(listaX)):
        [angleShoulder[step], angleElbow[step]] = ikArm(
            listaX[step] - hdist * aux[step], listaY[step], h)
        #aqui ploteabamos

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

    except ZeroDivisionError:
        #print "Divide by Zero error. No valid joint solution."
        return
    except ValueError:
        #print "Math function error. Probably square root of negative number. No valid joint solution."
        return

    theta = np.degrees(np.arctan2(float(y), float(x)) - np.arctan2(h * m, k))
    phi = np.degrees(np.arctan2(h * m, k) + np.arctan2(h * m, (d - k)))
    returnAngles = [theta, phi]
    return returnAngles


def lo_pass(sigC, cutoff):

    order = 3
    samprate = 2
    filtsig2 = np.ones((sigC.shape[0], sigC.shape[1])) * np.nan

    for m in range(len(sigC[0])):
        sig = sigC[:, m]
        a, b = scipy.signal.butter(
            order, (cutoff / (samprate / 2)), btype='low')
        filtsig2[:, m] = scipy.signal.filtfilt(b, a, sig)

    return filtsig2
