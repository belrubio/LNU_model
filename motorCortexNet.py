#!/usr/bin/python
import math
import random
import numpy as np

class Net:
    def __init__(self, sensitivity, cortex):
        self.sensitivity = sensitivity
        self.cortex = cortex
        self.activity = 0.0
        self.meanactivity = 0.0
        self.activity1 = 0.0
        self.weight = 0.0



    def tangArcFunc(self):
        sensitivity = self.sensitivity

        self.vx = math.cos(sensitivity)
        self.vy = math.sin(sensitivity)
        #print "vx ", self.vx, "     vy ", self.vy
        self.vx = self.activity*self.vx
        self.vy = self.activity*self.vy
        tangArc = (self.activity*self.vx,self.activity*self.vy)
        #self.activity = 0
        #tangArc = self.activity*np.array(tangArc)
        return tangArc, self.vx, self.vy

    def getExtent(self):
        sensitivity = self.sensitivity

        self.vx = math.cos(sensitivity)
        self.vy = math.sin(sensitivity)
        #print "vx ", self.vx, "     vy ", self.vy
        self.vx = self.activity*self.vx
        self.vy = self.activity*self.vy
        tangArc = (self.activity*self.vx,self.activity*self.vy)

        #self.activity = 0
        #tangArc = self.activity*np.array(tangArc)
        #if(np.linalg.norm(tangArc) < 0):
        #    act=0
        #else:
        act=np.linalg.norm(tangArc)
        return act

    def activationExtentRule_Func(self, targetextent):
        activityE = self.weight * (math.cos( min(targetextent-self.sensitivity, targetextent-self.sensitivity+2*math.pi, targetextent-self.sensitivity-2*math.pi, key=abs) ) )
        #print "activityE", activityE
        #no noise
        if(activityE>0.0):
            self.activity = activityE
        else:
            self.activity = 0.0
        return self.activity


    def activationRuleFunc(self, dAngle, meanactivity):
        activity1 =  math.cos(  min(dAngle-self.sensitivity, dAngle-self.sensitivity+2*math.pi, dAngle-self.sensitivity-2*math.pi, key=abs) )
        #activity1 =  min(dAngle-self.sensitivity, dAngle-self.sensitivity+2*math.pi, dAngle-self.sensitivity-2*math.pi, key=abs)

        #if(self.sensitivity > math.radians(270)):
        #print "activity1", math.degrees(activity1)
            

        #activity1 = math.cos( activity1 )

        #if (self.sensitivity > math.radians(270)):
        #print "sensitivity", math.degrees(self.sensitivity)
        #print "activity1-2", activity1

        #self.activity1 = activity1

        k = random.normalvariate(0, (0.15*activity1)) #noise
        #k=0.15

        
        activity = activity1 + k

        if (activity < 0):
            activity = 0

        self.activity = activity

        return activity, k

    #def synapticFunc(self, activList, dAngle):
    #    Act = []
    #    for q in range(100):
            #activity = self.activity
            #activity = self.activationRuleFunc(math.radians(dAngle))
    #        Act.append(activity)
        #w = linalg.lstsq(A.T,y)[0] # obtaining the parameters
    #    x = [i for i in range(360)]
    #    coeffs = np.polyfit(x , activList, deg=1)
    #    b = coeffs[1]
        #weight = self.activity - b   
    #    return b


    def activityFunc(self):
        activity = self.actitivity
        return activity


    def sensitivityFunc(self):
        sensitivity = self.sensitivity
        return sensitivity

    def learningRuleFunc(self, direction, dAngle, supervisedRation, unsupervisedRation):
        
        """
        angles = [(2*math.pi)-abs(dAngle-self.sensitivity),abs(dAngle-self.sensitivity)]
        smallerAngle =  angles.index(min(angles))
        smallerAngle2 = 0
        smallerAngle3 = 0

        #print "Angles", math.degrees(angles[0]), " ", math.degrees(angles[1])

        #print "SMALLER INDEX", smallerAngle
        
        if (smallerAngle == 0):
            if (dAngle<self.sensitivity):
                smallerAngle2 = ( abs ( (2*math.pi)-abs(dAngle-self.sensitivity) ) )
            else:
                smallerAngle2 = - abs( (2*math.pi)-abs(dAngle-self.sensitivity) )

        else:
            if(dAngle<self.sensitivity):
                smallerAngle2 = -( abs(dAngle-self.sensitivity) )
            else:
                smallerAngle2 = abs(dAngle-self.sensitivity)

        #print "smaller Angle2", math.degrees(smallerAngle2)

        angles = [(2*math.pi)-abs(dAngle-direction),abs(dAngle-direction)]
        smallerAngle =  angles.index(min(angles))

        if (smallerAngle == 0):
            if (dAngle<direction):
                smallerAngle3 = ( abs ( (2*math.pi)-abs(dAngle-direction) ) )
            else:
                smallerAngle3 = -(abs( (2*math.pi)-abs(dAngle-direction) ) )

        else:
            if(dAngle<direction):
                smallerAngle3 = -( abs(dAngle-direction) )
            else:
                smallerAngle3 = (abs(dAngle-direction) )

        #smallerAngle2=math.atan2(math.cos(dAngle-self.sensitivity), math.sin(dAngle-self.sensitivity))
        """

        smallerAngle2 = min(dAngle-self.sensitivity, dAngle-self.sensitivity+2*math.pi, dAngle-self.sensitivity-2*math.pi, key=abs)

        smallerAngle3= min(dAngle-direction, dAngle-direction+2*math.pi, dAngle-direction-2*math.pi, key=abs)

        #print "dangle ", math.degrees(dAngle)
        #print "direction", math.degrees(direction)
        #print "self.sensitivity ", math.degrees(self.sensitivity)
        #print "self.activity ", math.degrees(self.activity)
        #print " smallerAngle dAngle to -> sensitivity = ", math.degrees(smallerAngle2)
        #print " smallerAngle dAngle to -> direction = ", math.degrees(smallerAngle3)

        #print "SL : ", (supervisedRation * smallerAngle3 * self.activity)
        #print "UL : ", (unsupervisedRation * smallerAngle2 * self.activity)


        #if (dAngle<self.sensitivity):
        #        smallerAngle2 = -smallerAngle2

        #if (dAngle<direction):
        #        smallerAngle3 = -smallerAngle3

        self.sensitivity += (supervisedRation * smallerAngle3 * self.activity) + (unsupervisedRation * smallerAngle2 * self.activity)

        #self.sensitivity +=  (unsupervisedRation * smallerAngle2 * self.activity)

        if (self.sensitivity<0):
            self.sensitivity = self.sensitivity + (2*math.pi)
        else:
            if (self.sensitivity>=(2*math.pi)):
                self.sensitivity = self.sensitivity - (2*math.pi)
        #print "self.sensitivity ", math.degrees(self.sensitivity)
        #print "--------------------   --------------------"

        return self.sensitivity


    def learningRuleFunc_extent(self, error):

        weightLearning = 0.4
        self.weight += (weightLearning * error * self.activity)
        #print "ERROR:  ", error/100

