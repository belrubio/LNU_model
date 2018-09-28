#!/usr/bin/python
from main import * 

activListLeft = []
allTangSumLeft = []
tangSumLeft = [0,0]
errorListLeft = []
sumOfSquareActivitiesListLeft = []

activListRight = []
allTangSumRight = [0,0]
tangSumRight = [0,0]
errorListRight = []
sumOfSquareActivitiesListRight = []


def directionCodingFunc(leftCortex, rightCortex, newdAngle, N):
    
    vxsLeft = []
    vysLeft = []
    tangSumLeft = [0,0]
    acts = []

    mean_activity = 0

    #for i in range(len(leftCortex)):
    #    neuron_act=  math.cos(  min((2*math.pi)-abs(newdAngle-leftCortex[i].sensitivity), abs( newdAngle-leftCortex[i].sensitivity))  )
    #    if (neuron_act<0):
    #        neuron_act = 0
    #    mean_activity += neuron_act
    #mean_activity = mean_activity/len(leftCortex)

    #print "mean activily NO NOISE LEFT ::::= ", mean_activity

    #sum the tangentes of all the angles Left Cortex
    for i in range(len(leftCortex)):
        act, k = leftCortex[i].activationRuleFunc(newdAngle, mean_activity) # update activity of each cell
        #acts.append(act)
        #print "activity!  L ::::: ", act, "sd : ",  k

        a,x,y = leftCortex[i].tangArcFunc()
        vxsLeft.append(x)
        vysLeft.append(y)
        tangSumLeft[0] += x
        tangSumLeft[1] += y
        #print "tangSum L : ", tangSumLeft

        #print "all activities = ", acts

        allTangSumLeft.append(list(tangSumLeft))
    v1L = tangSumLeft
    #print "allTangSumLeft  ", allTangSumLeft
    v1 = tangSumLeft
    directionLeft = math.atan2(v1[1],v1[0])
    if(directionLeft < 0):
        directionLeft += (2*math.pi)
    if(directionLeft >= (2*math.pi)):
        directionLeft -= (2*math.pi)
    #print "directionLeft  ", math.degrees(directionLeft)
            
    #factor = 0.01/N
    #errorListLeft.append((((math.cos(min((2*math.pi)-abs(directionLeft-newdAngle), abs( directionLeft-newdAngle)))**2)/2)-factor*(sumOfSquareActivitiesLeft)**2))    

    #sum the tangentes of all the angles Right Cortex
    vxsRight = []
    vysRight = []
    tangSumRight = [0,0]

    mean_activity = 0

    #for i in range(len(rightCortex)):
    #        neuron_act= math.cos(  min((2*math.pi)-abs(newdAngle-rightCortex[i].sensitivity), abs( newdAngle-rightCortex[i].sensitivity))  )
    #        if (neuron_act<0):
    #            neuron_act = 0
    #        mean_activity += neuron_act

    #mean_activity = mean_activity/len(rightCortex)

    #print "mean activily NO NOISE RIGHT ::::= ", mean_activity


    for i in range(len(rightCortex)):
        act, k = rightCortex[i].activationRuleFunc(newdAngle, mean_activity) # update activity of each cell
        #print "activity!  R ::::: ", act, "sd : ",  k
        a,x,y = rightCortex[i].tangArcFunc()
        vxsRight.append(x)
        vysRight.append(y)
        tangSumRight[0] += x
        tangSumRight[1] += y
        #print "tangSumRight ", tangSumRight
        allTangSumRight.append(list(tangSumRight))
    v1R = tangSumRight
    #print "allTangSumRight", allTangSumRight
    v1 = tangSumRight
    directionRight = math.atan2(v1[1],v1[0])   # for range from 0 to 2pi ->    a = mod(atan2(y,x),2*pi);

    if(directionRight < 0):
        directionRight += (2*math.pi)
    if(directionRight >= (2*math.pi)):
        directionRight -= (2*math.pi)
    #factor = 0.01/N

    errorRight = ( min(newdAngle-directionRight, newdAngle-directionRight+2*math.pi, newdAngle-directionRight-2*math.pi, key=abs) )**2
    errorLeft = ( min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs) )**2

    #print "errorRight ---- > > > ", math.degrees(errorRight)
    #print "errorLeft ---- > > > ", math.degrees(errorLeft)


    #errorListRight.append((((math.cos(min((2*math.pi)-abs(directionRight-newdAngle), abs( directionRight-newdAngle)))**2)/2)-factor*(sumOfSquareActivitiesRight)**2))    

    v1L= v1L/ (np.sqrt(v1L[0]**2+v1L[1]**2))
    v1R= v1R/ (np.sqrt(v1R[0]**2+v1R[1]**2))

    return directionRight, directionLeft, errorListLeft ,errorListRight, allTangSumRight, allTangSumLeft, errorRight, errorLeft, v1L, v1R


def extentCodingFunc(leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_Extent, angleTarget):
    
    vxsLeft = []
    vysLeft = []
    tangSumLeft = 0
    acts = []

    mean_activity_e = 0

    #for i in range(len(leftCortex)):
    #    neuron_act=  math.cos(  min((2*math.pi)-abs(newdAngle-leftCortex[i].sensitivity), abs( newdAngle-leftCortex[i].sensitivity))  )
    #    if (neuron_act<0):
    #        neuron_act = 0
    #    mean_activity += neuron_act
    #mean_activity = mean_activity/len(leftCortex)

    #print "mean activily NO NOISE LEFT ::::= ", mean_activity

    #sum the tangentes of all the angles Left Cortex
    for i in range(len(leftCortex_extent)):
        #print "leftCortExtent: ", leftCortex_extent[i].sensitivity
        #acts.append(act)
        #print "activity!  L ::::: ", act, "sd : ",  k
        act = leftCortex_extent[i].activationExtentRule_Func(angleTarget) # update activity of each cell

        a = leftCortex_extent[i].getExtent()
        tangSumLeft += a
        #print "tangSum L : ", tangSumLeft

        #print "all activities = ", acts

        #allTangSumLeft.append(list(tangSumLeft))
    v1L = tangSumLeft
    #print "allTangSumLeft  ", allTangSumLeft
    v1 = tangSumLeft
    extentLeft = tangSumLeft
    #print "extentLeft", extentLeft

    
    #print "directionLeft  ", math.degrees(directionLeft)
            
    #factor = 0.01/N
    #errorListLeft.append((((math.cos(min((2*math.pi)-abs(directionLeft-newdAngle), abs( directionLeft-newdAngle)))**2)/2)-factor*(sumOfSquareActivitiesLeft)**2))    

    #sum the tangentes of all the angles Right Cortex
    vxsRight = []
    vysRight = []
    tangSumRight = 0

    mean_activity_e = 0

    #for i in range(len(rightCortex)):
    #        neuron_act= math.cos(  min((2*math.pi)-abs(newdAngle-rightCortex[i].sensitivity), abs( newdAngle-rightCortex[i].sensitivity))  )
    #        if (neuron_act<0):
    #            neuron_act = 0
    #        mean_activity += neuron_act

    #mean_activity = mean_activity/len(rightCortex)

    #print "mean activily NO NOISE RIGHT ::::= ", mean_activity


    for i in range(len(rightCortex_extent)):
        act = rightCortex_extent[i].activationExtentRule_Func(angleTarget) # update activity of each cell
        #print "activity!  R ::::: ", act, "sd : ",  k
        a = rightCortex_extent[i].getExtent()
        tangSumRight += a
        #print "tangSumRight ", tangSumRight
        #allTangSumRight.append(list(tangSumRight))
    v1R = tangSumRight
    #print "allTangSumRight", allTangSumRight
    v1 = tangSumRight
    extentRight = tangSumRight   # for range from 0 to 2pi ->    a = mod(atan2(y,x),2*pi);

    #factor = 0.01/N
    #print "ExtentR" , extentRight
    #print "ExtentL", extentLeft

    errorRight_e = newExtentR-extentRight
    errorLeft_e = newExtentL-extentLeft

    #print "errorRight ---- > > > ", errorRight_e
    #print "errorLeft ---- > > > ", errorLeft_e


    #errorListRight.append((((math.cos(min((2*math.pi)-abs(directionRight-newdAngle), abs( directionRight-newdAngle)))**2)/2)-factor*(sumOfSquareActivitiesRight)**2))    

    return extentRight, extentLeft, errorRight_e, errorLeft_e




if __name__ == "__directionCodingFunc__":
    directionCodingFunc()