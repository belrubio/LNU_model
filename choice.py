#!/usr/bin/python

from motorCortexNet import *
from actionChoiceNet import *
from main import *

nChoice = 10

def returnHandChoice(dAngle, choiceLeft, choiceRight,leftArm, rightArm, directionRight, directionLeft, trial, Exploration_Level):
	
	expectedRewardLeft = 0
	for i in range(len(choiceLeft)):
		#phi = math.exp(-((dAngle-math.radians(choiceLeft[i].center))**2/(math.pi/10)))
		phi = math.exp(-(((min(dAngle-choiceLeft[i].center, dAngle-choiceLeft[i].center+2*math.pi, dAngle-choiceLeft[i].center-2*math.pi, key=abs)**2))/((math.pi/10)**2)))
		#print "phi L ", phi
		expectedRewardLeft += (choiceLeft[i].weight * phi)

	expectedRewardRight = 0
	for i in range(len(choiceRight)):
		#phi = math.exp(-((math.radians(dAngle)-math.radians(choiceRight[i].center))**2/(math.pi/10)))
		phi = math.exp(-(((min(dAngle-choiceRight[i].center, dAngle-choiceRight[i].center+2*math.pi, dAngle-choiceRight[i].center-2*math.pi, key=abs)**2))/((math.pi/10)**2))) 
		#print "phi R ", phi

		expectedRewardRight += (choiceRight[i].weight * phi)

	#prevent overflow error:
	#if ((expectedRewardLeft-expectedRewardRight) > 60):
	#	probabilityOfActionLeft = 1
	#	probabilityOfActionRight = 0
	#else:
	#	if ((expectedRewardLeft-expectedRewardRight) < -60):
	#		probabilityOfActionLeft = 0
	#		probabilityOfActionRight = 1
	#	else:
	#print "expected R ", expectedRewardRight
	#print "expected L ", expectedRewardLeft
	
	probabilityOfActionLeft  =  1/(1+ (  math.exp(-Exploration_Level * (expectedRewardLeft - expectedRewardRight)) ) )
	probabilityOfActionRight  =  1/(1+ (  math.exp(-Exploration_Level * (expectedRewardRight - expectedRewardLeft)) ) )

	#print "------------------------"
	#print "probabilityOfActionLeft ", probabilityOfActionLeft

	goodLuck = float ( random.uniform(0,1) )

	#lateralization = 0.1
	if( goodLuck < probabilityOfActionLeft):
		#print "goodLuck = ", goodLuck
		#if ((90 < math.degrees(dAngle)) and ( math.degrees(dAngle) <=270)):
		#	choosenHand = 0
		#else:
		#	choosenHand = 1
		choosenHand = 0
	else:
		choosenHand = 1

	#CIT ->
	#if ( (trial>=500)and(trial<1500)):
	#	choosenHand = 1

	#print "choosenHand ", choosenHand

	lateralization_nonUsed = 0.2
	lateralization = 0.0

	if(choosenHand == 1): #RIGHT WORKSPACE
	
		prefWorkSpace = rightArm.prefWorkSpace
		#print "right prefWorkSpace ", prefWorkSpace[0], " ", prefWorkSpace[1]
		direction = directionLeft
		direction2=directionRight

		#print "dAngle in degrees here ", math.degrees(dAngle)
		if ((0 <= math.degrees(dAngle)) and (math.degrees(dAngle) <= prefWorkSpace[1])):
			lateralization_nonUsed = 0.0
			lateralization = 0.2
			#print " **** ipsilateral for angle 1", dAngle
		else:
		 	if((prefWorkSpace[0] <= math.degrees(dAngle)) and (math.degrees(dAngle)<= 360)):
		 		lateralization_nonUsed = 0.0
		 		lateralization = 0.2
				#print " **** ipsilateral for angle 2 ", dAngle

	else: # LEFT WORKSPACE
		prefWorkSpace = leftArm.prefWorkSpace
		direction = directionRight
		direction2 = directionLeft

		#print "left prefWorkSpace ", prefWorkSpace[0], " ", prefWorkSpace[1]
		if ((prefWorkSpace[0] <= math.degrees(dAngle)) and ( math.degrees(dAngle) <= prefWorkSpace[1])):
			lateralization_nonUsed = 0.0
			lateralization = 0.2
			#print " **** ipsilateral for angle ", dAngle

	#print "directionll ", math.radians(direction) , "  ", math.ceil(direction*100)/100

	#actualReward = math.ceil((math.exp(( ( math.radians(dAngle) - math.radians(direction))**2) / 0.2**2))*100)/100 + lateralization


	#print "error of direction selected ==== ", ( min(dAngle-direction, dAngle-direction+2*math.pi, dAngle-direction-2*math.pi, key=abs) **2)
	#print "total error reward selected==  ", math.exp( - ( min(dAngle-direction, dAngle-direction+2*math.pi, dAngle-direction-2*math.pi, key=abs) **2) / 0.2**2)
	#print "total error reward ==  ", math.exp( - ( min(dAngle-direction2, dAngle-direction2+2*math.pi, dAngle-direction2-2*math.pi, key=abs) **2) / 0.2**2)

	#To modify actual reward for paretic limb we update the direction Left for the amplifiedDirectionLeft from visual input
	#if ( (trial>500) and (trial<2500)):
	#	if(choosenHand==1):
	#		direction = dAngle;

	actualReward = math.exp( -(( min(dAngle-direction, dAngle-direction+2*math.pi, dAngle-direction-2*math.pi, key=abs) **2) / 0.2**2))

	#actualReward = math.exp( -(( min(dAngle-direction, dAngle-direction+2*math.pi, dAngle-direction-2*math.pi, key=abs) **2) / 0.2**2)) + lateralization
	#print " actual reward !! :", actualReward
	#print "lateralization", lateralization
	actualReward_nonUsed = math.exp( -(( min(dAngle-direction2, dAngle-direction2+2*math.pi, dAngle-direction2-2*math.pi, key=abs) **2) / 0.2**2)) + lateralization_nonUsed


	#print "1",choosenHand
	#print "2",actualReward
	#print "3",expectedRewardLeft
	#print "4",expectedRewardRight
	return choosenHand, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, probabilityOfActionLeft , probabilityOfActionRight, directionLeft
	

def CompetingAccumulators(accumulatorLeft, accumulatorRight, energies, expectedRewardLeft, expectedRewardRight):
	#print "energies : ", energies
	#print "expectedRewardRight", expectedRewardRight
	#print "expectedRewardLeft ->     -> ", expectedRewardLeft
	
	a = 0.4 # max expected reward is 1.2 and min is around 0.3
	b = 7 # CHANGED this in 2018-> 12 # max energies is 0.02 and min is 0.002
	c = 0.7
	HandSelected = -1
	#print "accumulate!!! "
	time.sleep(0.0001)

	#We add noise needed for exploration

	noise = float ( random.normalvariate(0,0.15) )
	accumulatorLeft_temp = accumulatorLeft + ( a*(expectedRewardLeft) - b*(energies[0]) ) + noise #energy 0 corresponds to left
	#noise = random.normalvariate(-0.05, 0.05)
	noise = float ( random.normalvariate(0,0.15) )
	accumulatorRight_temp = accumulatorRight +  ( a*(expectedRewardRight) - b*(energies[1]) ) + noise

	accumulatorLeft = accumulatorLeft_temp - c*accumulatorRight_temp 
	accumulatorRight = accumulatorRight_temp - c*accumulatorLeft_temp

	if(accumulatorLeft<0):
		accumulatorLeft = 0
	if(accumulatorRight<0):
		accumulatorRight=0
	
	#noise = random.normalvariate(-0.05, 0.05)
	#print "energiesLeft: ", energies[1]
	#print "energiesRight: ", energies[0]
	#print "expectedRewardLeft: ", expectedRewardLeft
	#print "expectedRewardRight: ", expectedRewardRight

	#print "accumulatorRight: ", accumulatorRight
	#print "accumulatorLeft: ", accumulatorLeft

	#probabilityOfActionLeft  =  1/(1+ (  math.exp(-10 * (expectedRewardLeft - expectedRewardRight)) ) )
	#probabilityOfActionRight  =  1/(1+ (  math.exp(-10 * (expectedRewardRight - expectedRewardLeft)) ) )

	if(accumulatorLeft > 1 or accumulatorRight > 1):
		if(accumulatorRight > accumulatorLeft):
			HandSelected=1
		else:
			if(accumulatorLeft > accumulatorRight):
				HandSelected=0
		
		#print "handSelected", HandSelected

	return HandSelected, accumulatorLeft, accumulatorRight


if __name__ == "__mainChoice__":
    mainChoice()

