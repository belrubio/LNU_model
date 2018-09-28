from SimulationsMain import *

allTangSumLeft = []
tangSumLeft = [0, 0]
errorListLeft = []
sumOfSquareActivitiesListLeft = []

activListRight = []
allTangSumRight = [0, 0]
tangSumRight = [0, 0]
errorListRight = []
sumOfSquareActivitiesListRight = []


def directionCodingFunc(leftCortex, rightCortex, newdAngle, N):

    vxsLeft = []
    vysLeft = []
    tangSumLeft = [0, 0]
    acts = []
    mean_activity = 0

    #sum the tangentes of all the angles Left Cortex
    for i in range(len(leftCortex)):
        act, k = leftCortex[i].activationRuleFunc(
            newdAngle, mean_activity)  # update activity of each cell
        a, x, y = leftCortex[i].tangArcFunc()
        vxsLeft.append(x)
        vysLeft.append(y)
        tangSumLeft[0] += x
        tangSumLeft[1] += y

        allTangSumLeft.append(list(tangSumLeft))

    v1L = tangSumLeft
    v1 = tangSumLeft
    directionLeft = math.atan2(v1[1], v1[0])
    if (directionLeft < 0):
        directionLeft += (2 * math.pi)
    if (directionLeft >= (2 * math.pi)):
        directionLeft -= (2 * math.pi)

    #sum the tangents of all the angles Right Cortex
    vxsRight = []
    vysRight = []
    tangSumRight = [0, 0]

    mean_activity = 0

    for i in range(len(rightCortex)):
        act, k = rightCortex[i].activationRuleFunc(
            newdAngle, mean_activity)  # update activity of each cell
        a, x, y = rightCortex[i].tangArcFunc()
        vxsRight.append(x)
        vysRight.append(y)
        tangSumRight[0] += x
        tangSumRight[1] += y
        allTangSumRight.append(list(tangSumRight))

    v1R = tangSumRight
    v1 = tangSumRight
    directionRight = math.atan2(
        v1[1],
        v1[0])  # for range from 0 to 2pi ->    a = mod(atan2(y,x),2*pi);

    if (directionRight < 0):
        directionRight += (2 * math.pi)
    if (directionRight >= (2 * math.pi)):
        directionRight -= (2 * math.pi)

    # Compute errors and Vectors
    errorRight = (min(
        newdAngle - directionRight,
        newdAngle - directionRight + 2 * math.pi,
        newdAngle - directionRight - 2 * math.pi,
        key=abs))**2
    errorLeft = (min(
        newdAngle - directionLeft,
        newdAngle - directionLeft + 2 * math.pi,
        newdAngle - directionLeft - 2 * math.pi,
        key=abs))**2
    v1L = v1L / (np.sqrt(v1L[0]**2 + v1L[1]**2))
    v1R = v1R / (np.sqrt(v1R[0]**2 + v1R[1]**2))

    return directionRight, directionLeft, errorListLeft, errorListRight, allTangSumRight, allTangSumLeft, errorRight, errorLeft, v1L, v1R


def extentCodingFunc(leftCortex_extent, rightCortex_extent, newExtentL,
                     newExtentR, N_Extent, angleTarget):

    vxsLeft = []
    vysLeft = []
    tangSumLeft = 0
    acts = []
    mean_activity_e = 0

    for i in range(len(leftCortex_extent)):
        act = leftCortex_extent[i].activationExtentRule_Func(
            angleTarget)  # update activity of each cell

        a = leftCortex_extent[i].getExtent()
        tangSumLeft += a

    v1L = tangSumLeft
    v1 = tangSumLeft
    extentLeft = tangSumLeft

    #sum the tangentes of all the angles Right Cortex
    vxsRight = []
    vysRight = []
    tangSumRight = 0

    mean_activity_e = 0

    for i in range(len(rightCortex_extent)):
        act = rightCortex_extent[i].activationExtentRule_Func(
            angleTarget)  # update activity of each cell
        a = rightCortex_extent[i].getExtent()
        tangSumRight += a

    v1R = tangSumRight
    v1 = tangSumRight
    extentRight = tangSumRight  # for range from 0 to 2pi ->    a = mod(atan2(y,x),2*pi);

    errorRight_e = newExtentR - extentRight
    errorLeft_e = newExtentL - extentLeft

    return extentRight, extentLeft, errorRight_e, errorLeft_e


if __name__ == "__directionCodingFunc__":
    directionCodingFunc()
