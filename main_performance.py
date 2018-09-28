#!/usr/bin/python
import numpy as np
from pylab import plot,show
import pprint, random, time
import matplotlib.pyplot as plt
from motorCortexNet import *
from actionChoiceNet import *
from choice import *
from armReward import *
from directionCoding import * 
import json

trials = 360

def main():

    f=json.loads(open('weightsTraining_v5.json').read())

    sensitivityUpdateRight = []
    sensitivityUpdateLeft = []

    N = 500
    dAngle = 180
    leftCortex  = [ Net(math.radians(f['sensitivityUpdateLeft'][i]), "left") for i in range(N)]
    rightCortex = [ Net(math.radians(f['sensitivityUpdateRight'][i]), "right") for i in range(N)]


    #Generating stroke: we remove 50% of neurons in left cortex
    #for i in range(N/2):
    #    del leftCortex[i+(N/4)]


    #print 'sensitivityUpdateLeft', f['sensitivityUpdateLeft']

    spatialRangeLeft  = (90,270)
    spatialRangeRight = (270,90)

    rightArm = ArmRewardClass("right", 0, spatialRangeRight)
    leftArm = ArmRewardClass("left", 0 , spatialRangeLeft)

    probability_right = []       
    probability_left = []
    listOfAngles = []


    ######## action choice nets #########
    Nchoice = 10
    pi=math.pi

    choiceLeft = [ ActionChoiceClass("left", (i*2*pi/Nchoice), f['weightListCheckLeft'][i], 0 ) for i in range(Nchoice)] 

    choiceRight= []
    for i in range(Nchoice):
        if (i < Nchoice/2):
            centerRBF = 3*pi/2 + i*pi/Nchoice
        else:
            centerRBF = i*pi/Nchoice - math.radians(90)

        choiceRight.append ( ActionChoiceClass("right", (i*2*pi/Nchoice), f['weightListCheckRight'][i], 0 ))

    weightListCheckLeft = []
    weightListCheckRight = []


    for e in range(trials):
    	#newdAngle = dAngle
    	newdAngle = math.radians(dAngle - (int(random.uniform(-180,180))))
    	#print "------------------"
        print "New dAngle ---", math.degrees(newdAngle), " ------->"
    	###########################
    	#### direction Conding ####
    	###########################
    	directionRight, directionLeft, errorListLeft ,errorListRight = directionCodingFunc( leftCortex, rightCortex, newdAngle, N)
    	#compute the hand choice:

        #print "directionRight  ", math.degrees(directionRight)

        #print "directionLeft  ", math.degrees(directionLeft)
    
        
    	#choosenHand, actualReward, expectedRewardLeft, expectedRewardRight = 
    	[choosenHand, actualReward, expectedRewardLeft, expectedRewardRight, p_left, p_right] = returnHandChoice(newdAngle , choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft)
    	#print "2",actualReward

        probability_right.append(p_right)        
        probability_left.append(p_left)
        listOfAngles.append(math.degrees(newdAngle))


    	#returnHandDict = returnHandChoice(dAngle , choiceLeft , choiceRight)
    	#print "...." ,expectedRewardRight
    	#print "---> ", returnHandChoice(dAngle , choiceLeft , choiceRight) , "<---"

    	if (e == trials-1):
			for p in range(len(choiceLeft)):
				weightListCheckLeft.append(choiceLeft[p].weight)
				weightListCheckRight.append(choiceRight[p].weight)

        if(choosenHand==0):
        #if(True):
            print "hand left"

            sensitivityUpdateLeft = []
            sumOfSquareActivitiesLeft = 0
            for i in range(len(leftCortex)):
                sumOfSquareActivitiesLeft += leftCortex[i].activity
                sensitivityUpdateLeft.append(math.degrees(leftCortex[i].learningRuleFunc(directionLeft, newdAngle)))
                #leftCortex[i].activity = 0 #reset activity of the neuron for next trial

            #print " sum acts LEFT ", sumOfSquareActivitiesLeft
            sumOfSquareActivitiesListLeft.append(sumOfSquareActivitiesLeft)


        if(choosenHand==1):
        #if(True):
            print "hand right"
            sensitivityUpdateRight = []
            sumOfSquareActivitiesRight = 0

            for i in range(len(rightCortex)):
                sumOfSquareActivitiesRight += rightCortex[i].activity
                sensitivityUpdateRight.append(math.degrees(rightCortex[i].learningRuleFunc(directionRight, newdAngle)))
                #   rightCortex[i].activity = 0 #reset activity of the neuron for next trial

            #print "sum acts RIGHT ", sumOfSquareActivitiesRight
            sumOfSquareActivitiesListRight.append(sumOfSquareActivitiesRight)

        #print "indent "
        #### Action value update ###
        
        
        #print "rightArm.actionValue ", rightArm.actionValue
        #print "leftArm.actionValue ", leftArm.actionValue
		
        if(choosenHand==0):
            leftArm.actionValue = actualReward-expectedRewardLeft
            # cortex left
            for i in range(len(choiceLeft)):
        	   #choiceLeft[i].weight += 0.1* leftArm.actionValue * math.exp( -((math.radians(newdAngle))  - math.radians(choiceLeft[i].center) )**2 / (math.pi/10))
        	   #choiceLeft[i].weight  += 0.1* leftArm.actionValue * math.exp( -((math.radians(newdAngle))  - math.radians(choiceLeft[i].center) )**2 / (math.pi/10)**2)
                choiceLeft[i].weight  += 0.1* leftArm.actionValue * math.exp( -  ( ( (min((2*math.pi)-abs(newdAngle-choiceLeft[i].center), abs( newdAngle-choiceLeft[i].center)))**2) / (math.pi/10)**2) )

        if(choosenHand==1):
            rightArm.actionValue = actualReward-expectedRewardRight

            # cortex right
            for i in range(len(choiceRight)):
                choiceRight[i].weight  += 0.1* rightArm.actionValue * math.exp( -  (  ( (min((2*math.pi)-abs(newdAngle-choiceRight[i].center), abs( newdAngle-choiceRight[i].center)))**2) / (math.pi/10)**2) )
	

    #dictWeights = { 'weightListCheckLeft' : weightListCheckLeft, 'weightListCheckRight' : weightListCheckRight, 'sensitivityUpdateLeft':sensitivityUpdateLeft , 'sensitivityUpdateRight' : sensitivityUpdateRight}

    #with open('weightsTraining_v4.json', 'wb') as f:
    #    #save training weights to file
    #    json.dump(dictWeights,f)
    
    meanProbLeft = []
    meanProbRight = []


    #print "weightsR", weightListCheckRight
    #print "weightsL", weightListCheckLeft
    #print "sensitivityUpdateLeft", sensitivityUpdateLeft
    #print "sensitivityUpdateRight", sensitivityUpdateRight

    if(e>=(trials-360)):
        for j in range(360):
            sl=0
            sr=0
            ind = [i for i,val in enumerate(listOfAngles) if val==j]
            for h in range(len(ind)):
                element = ind[h]
                sl=probability_left[element]
                sr=probability_right[element]
                
            meanProbLeft.append(sl)
            meanProbRight.append(sr)

    ######## plots #########
    #fig0 = plt.figure("performance error right")
    plt.figure()#figsize=(6, 4))
    plt.subplot(1, 2, 1)
    plt.plot( errorListRight , '-o') # [i for i in range(len(errorListRight))]  ,  errorListRight , '-o' )

    plt.subplot(1, 2, 2)
    plt.plot( errorListLeft , '-o' ) 
    #plt.plot( [i for i in range(len(errorListLeft))]  ,  errorListLeft , '-o' )

    #plt.tight_layout()
    plt.show()
    #fig10 = plt.figure("performance error left")
    #plt.subplot( [i for i in range(len(errorListLeft))]  ,  errorListLeft , '-o' )
    #plt.show()


    #fig1 = plt.figure("vector")
    #x_list = [l[0] for l in allTangSum ]
    #y_list = [l[1] for l in allTangSum ]
    #plt.plot(x_list, y_list, '-o')
    #plt.show()
    

    fig20 = plt.figure("sensitivityUpdateLeft")   
    xx = [h for h in range(len(sensitivityUpdateLeft))]
    plt.plot( xx, sensitivityUpdateLeft)
    fig20.canvas.draw()
    #plt.show()
       
    fig2 = plt.figure("sensitivityUpdateRight")   
    xx = [h for h in range(len(sensitivityUpdateRight))]
    plt.plot( xx, sensitivityUpdateRight)
    fig2.canvas.draw()
    plt.show()
    


    #print "Sensitivities Right", sensitivityUpdateRight

    #print "Sensitivities Left", sensitivityUpdateLeft


    
    fig3 = plt.figure("weightListCheckRight")   
    xx = [h for h in range(len(weightListCheckRight))]
    plt.plot( xx, weightListCheckRight, '-or')
    fig3.canvas.draw()
    plt.plot( xx, weightListCheckLeft, '-ob')
    fig3.canvas.draw()
    plt.show()

    fig4 = plt.figure("Probabilities Per Angle 0 to 360")   
    xx = [h for h in range(len(meanProbLeft))]
    plt.subplot(1, 2, 1)
    plt.plot( xx, meanProbRight, '-or')
    plt.subplot(1, 2, 2)
    plt.plot( xx, meanProbLeft, '-ob')
    plt.show()
    

if __name__ == "__main__":
	main()