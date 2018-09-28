#!/Users/lowly/anaconda/bin/python
import sys
sys.path.append('/Library/Python/2.7/site-packages/matplotlib-1.3.1-py2.7-macosx-10.8-intel.egg/')
import numpy as np
#from pylab import plot,show
import pprint, random, time
import matplotlib.pyplot as plt
from motorCortexNet import *
from actionChoiceNet import *
from choice import *
from armReward import *
from directionCoding import * 
import json
import calculaterEnergies_v1
import _thread


 
def SimulationsMain():

    trials = 2000 # FREEPARAM
    energies = [0, 0]

    sensitivityUpdateRight = []
    sensitivityUpdateLeft = []

    N = 500
    leftCortex  = [ Net(math.radians(i*float(360.00/N)), "left") for i in range(N)]
    rightCortex = [ Net(math.radians(i*float(360.00/N)), "right") for i in range(N)]
    N_extent = 20
    #100 amplitude sensitivities
    leftCortex_extent  = [ Net(math.radians(i*float(360.00/N_extent)), "left") for i in range(N_extent)]
    rightCortex_extent = [ Net(math.radians(i*float(360.00/N_extent)), "right") for i in range(N_extent)]
    for i in range(N_extent):
        leftCortex_extent[i].weight = 0.3 # update activity of each cell
        rightCortex_extent[i].weight = 0.3 # update activity of each cell

    spatialRangeLeft = (90,270)
    spatialRangeRight = (270,90)

    rightArm = ArmRewardClass("right", 0, spatialRangeRight)
    leftArm = ArmRewardClass("left", 0 , spatialRangeLeft)

    probability_right = []
    probability_left = []
    listOfAngles = []
    rt = []
    angle_per_trial = []
    choosen_per_trial = []
    errorLeft_extent = []
    errorRight_extent = []
    errorLeft_angle = []
    errorRight_angle = []
    expected_L = []
    expected_R = []
    energy_L = []
    energy_R = []
    actualReward_logs = []

    ######## action choice nets #########
    Nchoice = 10  # FREEPARAM
    pi=math.pi
 
    #choiceLeft = [ ActionChoiceClass("left", (math.radians(90)+(i*pi/Nchoice)), 0, 0 ) for i in range(Nchoice)] 

    #choiceRight= []
    #choiceRight= []
    #for i in range(Nchoice):
    #    if (i < Nchoice/2):
    #        centerRBF = (pi+pi/2) + i*pi/Nchoice
    #    else:
    #        centerRBF = i*pi/Nchoice - math.radians(90)

    #    choiceRight.append ( ActionChoiceClass("right", centerRBF, 0, 0 ))

    choiceRight = []
    choiceLeft = []

    #for h in range(2):
    #    for i in range(Nchoice/2):
    #        choiceRight.append ( ActionChoiceClass("right", (i*2*pi/Nchoice/2), 1, 0 ))
    #        choiceLeft.append ( ActionChoiceClass("left", (i*2*pi/Nchoice/2), 1, 0 ))


    #weights should be initialized to...
    choiceLeft = [ ActionChoiceClass("left", (i*2*pi/Nchoice),0.5,0) for i in range(Nchoice)]
    choiceRight= [ ActionChoiceClass("right", (i*2*pi/Nchoice),0.5,0) for i in range(Nchoice)]

    # for i in range(Nchoice):
    #     print "right", math.degrees(choiceRight[i].center)

    # for i in range(Nchoice):
    #     print "left", math.degrees(choiceLeft[i].center)

    weightListCheckLeft = []
    weightListCheckRight = []


    nInput = 250 # FREEPARAM


    possibleAngles = [ (i*float(360.00/nInput)) for i in range(nInput)]
    #print "possibleAngles", possibleAngles

    #suffle PissibleAnles
    for x in range(nInput):
        auxShuffle = int ( random.uniform(0,nInput) )
        auxShuffle_2 = possibleAngles[auxShuffle]
        possibleAngles[auxShuffle] = possibleAngles[x]
        possibleAngles[x] = auxShuffle_2

    #print (len(leftCortex))


    for e in range(trials):
    	#newdAngle = dAngle
        #r = int(random.uniform(0,500))
    	#newdAngle = math.radians(random.uniform(0,360))
        newdAngle = math.radians(possibleAngles[e%nInput])

        if((e%nInput) == 0 ):
            for x in range(nInput):
                auxShuffle = int ( random.uniform(0,nInput) )
                auxShuffle_2 = possibleAngles[auxShuffle]
                possibleAngles[auxShuffle] = possibleAngles[x]
                possibleAngles[x] = auxShuffle_2

    	#print "------------------"
        #newdAngle = 0.02
        #print "New dAngle ---", math.degrees(newdAngle), " ------->"
    	###########################
    	#### direction Conding ####
    	###########################
        a=[ (-0.2+math.cos(newdAngle)), (math.sin(newdAngle))]
        newExtentR = np.linalg.norm(a)
        b=[ (0.2+math.cos(newdAngle) ), (math.sin(newdAngle))]
        newExtentL = np.linalg.norm(b)

        startTime = int(round(time.time() * 1000))
        choosenHand = -1;
        acL = 0
        acR = 0

        # print "newExtentL : ", newExtentL
        # print "newExtentR : ", newExtentR

        directionRight, directionLeft, errorListLeft ,errorListRight, allTangSumR, allTangSumL, errorR, errorL, dvL, dvR = directionCodingFunc( leftCortex, rightCortex, newdAngle, N)

        extentRight, extentLeft, errorRight_e, errorLeft_e = extentCodingFunc( leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_extent, newdAngle)

        while(choosenHand == -1):
            currT = int(round(time.time() * 1000))

            [energies, angleShoulder, angleElbow] = calculaterEnergies_v1.fComputeEnergies(np.vstack((dvR, dvL))/3., newdAngle, extentRight, extentLeft)
            [choosenH, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, p_left, p_right, directionLeft_Amp] = returnHandChoice(newdAngle , choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft, 0)
        
            [choosenHand, acL, acR] = CompetingAccumulators(acL, acR, energies, expectedRewardLeft, expectedRewardRight)

        # print "choosenHand", choosenHand, "-------------"

        # print "extentRight", extentRight
        # print "extentLeft", extentLeft

        # print "expectedRewardLeft", expectedRewardLeft, "-------*******------"
        # print "expectedRewardRight", expectedRewardRight, "-------*******------"

        # print "energy_R", energies[1]
        # print "energy_L", energies[0]


        rt.append(currT - startTime)
        choosen_per_trial.append(choosenHand)
        angle_per_trial.append(newdAngle)
        errorLeft_extent.append(errorLeft_e)
        errorRight_extent.append(errorRight_e)
        errorLeft_angle.append(min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs))
        errorRight_angle.append(min(newdAngle-directionRight, newdAngle-directionRight+2*math.pi, newdAngle-directionRight-2*math.pi, key=abs))
        expected_L.append(expectedRewardLeft)
        expected_R.append(expectedRewardRight)
        energy_L.append(energies[1])
        energy_R.append(energies[0])

        if (e == trials-1):
            for p in range(len(choiceLeft)):
                weightListCheckLeft.append(choiceLeft[p].weight)
                weightListCheckRight.append(choiceRight[p].weight)

        if(choosenHand==0):
            actualReward = math.exp( -(( min(newdAngle-directionRight, newdAngle-directionRight+2*math.pi, newdAngle-directionRight-2*math.pi, key=abs) **2) / 0.2**2)) - (math.sqrt(errorRight_e**2)*0.1)
        else:
            actualReward = math.exp( -(( min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs) **2) / 0.2**2)) - (math.sqrt(errorLeft_e**2)*0.1)

        actualReward_logs.append(actualReward)


        #predictionErrorL = actualReward - (errorLeft_e*0.2) - (energies[1]*20) - expectedRewardLeft
        #predictionErrorR = actualReward - (errorRight_e*0.2) - (energies[0]*20) - expectedRewardRight
    
        predictionErrorL = actualReward - expectedRewardLeft
        predictionErrorR = actualReward - expectedRewardRight

        #if (e<2001):
    
        if(choosenHand==1):
    
            #print "actual reward", actualReward
            #print "actual reward nonUsed", actualReward_nonUsed
    
            #print "leftArm.actionValue", leftArm.actionValue
            #print "rightArm.actionValue", rightArm.actionValue
     
            # cortex left
            for i in range(len(choiceRight)):
                #choiceLeft[i].weight += 0.1* leftArm.actionValue * math.exp( -((math.radians(newdAngle))  - math.radians(choiceLeft[i].center) )**2 / (math.pi/10))
                #choiceLeft[i].weight  += 0.1* leftArm.actionValue * math.exp( -((math.radians(newdAngle))  - math.radians(choiceLeft[i].center) )**2 / (math.pi/10)**2)
                #choiceLeft[i].weight  += 0.1 * predictionErrorL * math.exp( -  ( (min(newdAngle-choiceLeft[i].center, newdAngle-choiceLeft[i].center+2*math.pi, newdAngle-choiceLeft[i].center-2*math.pi, key=abs)**2) / (math.pi/10.0)**2) ) 
                choiceRight[i].weight  += 0.1 * predictionErrorR * math.exp( -  (  ( min(newdAngle-choiceRight[i].center, newdAngle-choiceRight[i].center+2*math.pi, newdAngle-choiceRight[i].center-2*math.pi, key=abs))**2 / (math.pi/10)**2) )
                # FREEPARAM


        if(choosenHand==0):
    
            #print "actual reward", actualReward
            #print "actual reward nonUsed", actualReward_nonUsed
    
            # cortex right
            for i in range(len(choiceRight)):
                choiceLeft[i].weight  += 0.1 * predictionErrorL * math.exp( -  (  ( min(newdAngle-choiceLeft[i].center, newdAngle-choiceLeft[i].center+2*math.pi, newdAngle-choiceLeft[i].center-2*math.pi, key=abs))**2 / (math.pi/10)**2) )
                #choiceRight[i].weight  += 0.1 * predictionErrorR * math.exp( -  (  ( min(newdAngle-choiceRight[i].center, newdAngle-choiceRight[i].center+2*math.pi, newdAngle-choiceRight[i].center-2*math.pi, key=abs)**2) / (math.pi/10.0)**2) )
    
                #if(e>1995):
                    #print "R Weights"
                    #print choiceRight[i].weight
                    #print "L Weights"
                    #print choiceLeft[i].weight
    
    
        if(choosenHand==1):
        #if(True):    
            sensitivityUpdateLeft = []
            sumOfSquareActivitiesLeft = 0
            for i in range(len(leftCortex)):
                sumOfSquareActivitiesLeft += leftCortex[i].activity
                sensitivityUpdateLeft.append(math.degrees(leftCortex[i].learningRuleFunc(directionLeft, newdAngle)))
            for i in range(len(leftCortex_extent)):
                leftCortex_extent[i].learningRuleFunc_extent( errorLeft_e)
                
            #leftCortex[i].activity = 0 #reset activity of the neuron for next trial

            #print " sum acts LEFT ", sumOfSquareActivitiesLeft
            sumOfSquareActivitiesListLeft.append(sumOfSquareActivitiesLeft)


        if(choosenHand==0):
        #if(True):
            sensitivityUpdateRight = []
            sumOfSquareActivitiesRight = 0
    
            for i in range(len(rightCortex)):
                sumOfSquareActivitiesRight += rightCortex[i].activity
                sensitivityUpdateRight.append(math.degrees(rightCortex[i].learningRuleFunc( directionRight, newdAngle)))
            for i in range(len(rightCortex_extent)):
                rightCortex_extent[i].learningRuleFunc_extent( errorRight_e )
                #   rightCortex[i].activity = 0 #reset activity of the neuron for next trial
    
            #print "sum acts RIGHT ", sumOfSquareActivitiesRight
            sumOfSquareActivitiesListRight.append(sumOfSquareActivitiesRight)

        #if(e==100):
        #    print "###### trial 100 #######"

        #if (e==1990):
        #    print "###### trial 1990 #######"

        

    p_right=0
    p_left=0
    probability_right = []
    probability_left = []
    error_right = []
    error_left = []
    error_extent_right = []
    error_extent_left = []
    error = []
    weight_extent_Left = []
    weight_extent_Right = []

    for i in range(nInput):
        angle = math.radians(possibleAngles[i])
        #newExtentL = math.sqrt( ((-0.3+math.cos(angle))**2) + (math.sin(angle)**2) )
        #newExtentR = math.sqrt( ((0.3+math.cos(angle))**2) + (math.sin(angle)**2) )
        a=[ (-0.2+math.cos(angle)), (math.sin(angle))]
        newExtentR = np.linalg.norm(a)
        b=[ (0.2+math.cos(angle) ), (math.sin(angle))]
        newExtentL = np.linalg.norm(b)
        directionRight, directionLeft, errorListLeft ,errorListRight, b, c, errorR, errorL, dvL, dvR = directionCodingFunc( leftCortex, rightCortex, angle, N)
        [choosenHand, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, p_left, p_right, directionLeft_Amp] = returnHandChoice(angle, choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft, 0)
        probability_right.append(p_right)        
        probability_left.append(p_left)
        error_right.append(errorR)
        error_left.append(errorL)
        extentRight, extentLeft, errorRight_e, errorLeft_e = extentCodingFunc( leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_extent, newdAngle)
        error_extent_right.append(errorRight_e)
        error_extent_left.append(errorLeft_e)
        if (p_right > p_left):
            error.append(errorR)
        else:
            error.append(errorL)

    #print "possAngles", possibleAngles
    #print "pR list", probability_right
    #print "pL list", probability_left


    sensitivityLeft = []
    sensitivityRight = []
    for j in range(N):
        sensitivityLeft.append (math.degrees(leftCortex[j].sensitivity) )
        sensitivityRight.append(math.degrees(rightCortex[j].sensitivity) )

    for j in range(N_extent):
        weight_extent_Left.append(leftCortex_extent[j].weight)
        weight_extent_Right.append(rightCortex_extent[j].weight)

    #dictWeights = { 'weightListCheckLeft' : weightListCheckLeft, 'weightListCheckRight' : weightListCheckRight, 'sensitivityUpdateLeft':sensitivityLeft , 'sensitivityUpdateRight' : sensitivityRight, 'weight_extent_R': weight_extent_Right, 'weight_extent_L': weight_extent_Left}
    dictWeights = { 'weightListCheckLeft' : weightListCheckLeft, 'weightListCheckRight' : weightListCheckRight, 'sensitivityUpdateLeft':sensitivityLeft , 'sensitivityUpdateRight' : sensitivityRight, 'weight_extent_R': weight_extent_Right, 'weight_extent_L': weight_extent_Left, "error_extent_right": error_extent_right, "error_extent_left": error_extent_left, "error_right": error_right, "error_left": error_left}

    with open('Training_v29_model.json', 'wb') as f:
        #save training weights to file
        json.dump(dictWeights,f)
    
    meanProbLeft = []
    meanProbRight = []


    dictWeights = { 'meanProbRight' : probability_right, 'meanProbLeft' : probability_left, 'listOfAngles' : listOfAngles}

    with open('Training_v29_probability.json', 'wb') as file:
        #save training weights to file
        json.dump(dictWeights,file)


    # print "weightsR", weightListCheckRight
    # print "weightsL", weightListCheckLeft
    #print "sensitivityUpdateLeft", sensitivityUpdateLeft
    #print "sensitivityUpdateRight", sensitivityUpdateRight

    dictLogs = { 'Choosen' : choosen_per_trial, 'angle_per_trial' : angle_per_trial, 'rt' : rt, 'errorLeft_extent':errorLeft_extent, 'errorRight_extent':errorRight_extent,  'errorLeft_angle':errorLeft_angle, 'errorRight_angle':errorRight_angle, 'expected_L':expected_L, 'expected_R': expected_R, 'energy_L': energy_L, 'energy_R': energy_R, 'actualReward_logs':actualReward_logs}
    with open('Training_v29_logs.json', 'wb') as file:
        #save training weights to file
        json.dump(dictLogs,file)


    #for j in range(nInput):
    #    sl=0
    #    sr=0
    #    for x in range(nInput):
    #        if (listOfAngles[x] == possibleAngles[j]):
    #            meanProbRight.append(probability_left[x]) #probabilities selecting RIGHT hand = LEFT cortex
    #            meanProbLeft.append(probability_right[x]) 

    #for j in range(nInput):
    #    sl=0
    #    sr=0
    #    ind = [i for i,val in enumerate(listOfAngles) if val==j]
    #    for h in range(len(ind)):
    #        element = ind[h]
    #        sl=probability_left[element]
    #        sr=probability_right[element]
    #        
    #    meanProbRight.append(sl) #probabilities selecting RIGHT hand = LEFT cortex
    #    meanProbLeft.append(sr) 

    ######## plots #########
    #fig0 = plt.figure("performance error right")
    #plt.figure()#figsize=(6, 4))
    #plt.subplot(1, 2, 1)
    #plt.plot( errorListRight , '-o') # [i for i in range(len(errorListRight))]  ,  errorListRight , '-o' )

    #plt.subplot(1, 2, 2)
    #plt.plot( errorListLeft , '-o' ) 
    #plt.plot( [i for i in range(len(errorListLeft))]  ,  errorListLeft , '-o' )

    #plt.tight_layout()
    #plt.show()
    #fig10 = plt.figure("performance error left")
    #plt.subplot( [i for i in range(len(errorListLeft))]  ,  errorListLeft , '-o' )
    #plt.show()


    #fig1 = plt.figure("vector")
    #x_list = [l[0] for l in allTangSum ]
    #y_list = [l[1] for l in allTangSum ]
    #plt.plot(x_list, y_list, '-o')
    #plt.show()
    

    fig20 = plt.figure("sensitivityUpdateLeft")   
    xx = [h for h in range(len(sensitivityLeft))]
    plt.plot( xx, sensitivityUpdateLeft)
    fig20.canvas.draw()
    #plt.show()
       
    fig2 = plt.figure("sensitivityUpdateRight")   
    xx = [h for h in range(len(sensitivityRight))]
    plt.plot( xx, sensitivityUpdateRight)
    fig2.canvas.draw()
    plt.show()
    


    #print "Sensitivities Right length ", len(sensitivityUpdateRight), " val  ",  sensitivityUpdateRight
    #print "Sensitivities Left length ", len(sensitivityUpdateLeft), "  val ", sensitivityUpdateLeft


    fig3 = plt.figure("weightListCheckRight=red")   
    xx = [h for h in range(len(weightListCheckRight))]
    plt.plot( xx, weightListCheckRight, '-or')
    fig3.canvas.draw()
    plt.plot( xx, weightListCheckLeft, '-ob')
    fig3.canvas.draw()
    plt.show()

    fig4 = plt.figure("weights EXTENT.Right=red")   
    xx = [h for h in range(len(weight_extent_Right))]
    plt.plot( xx, weight_extent_Right, '-or')
    fig3.canvas.draw()
    plt.plot( xx, weight_extent_Left, '-ob')
    fig3.canvas.draw()
    plt.show()





    ## -------------- PLOTS ----------------------------------

    fileStroke=json.loads(open('Training_v29_probability.json').read())
    probability_right = []
    probability_left = []
    listOfAngles = []

    for i in range(nInput):
        #    print fileStroke['meanProbRight'][i]
        #    print i
        probability_right.append(fileStroke['meanProbRight'][i])
        probability_left.append(fileStroke['meanProbLeft'][i])
        listOfAngles.append( math.radians(possibleAngles[i]) )


        #probability_left.append(fileStroke['meanProbLeft'][i])


    

    """
    for i in range(500):
        for j in range(500):
            if (listOfAngles[i]>listOfAngles[j]):
                aux=listOfAngles[i]
                listOfAngles[i] = listOfAngles[j]
                listOfAngles[j] = aux

                aux=probability_left[i]
                probability_left[i] = probability_left[j]
                probability_left[j] = aux

                aux=probability_right[i]
                probability_right[i] = probability_right[j]
                probability_right[j] = aux
    """
    
    
    # print len(probability_right)
    # print len(probability_left)

    neu = 0

    angL = []
    angR = []

    #print "probability_right", probability_right
    #print "probability_left", probability_left

    #print "listOfAngles", listOfAngles

    for i in range(nInput):
        if (probability_left[i]>0.5):
            angL.append(listOfAngles[i])

        else:
            #if (probability_left[i]==0.5):
            #    angL.append(listOfAngles[i])
            #    angR.append(listOfAngles[i])

            if(probability_right[i]>0.5):
                angR.append(listOfAngles[i])


        #print "ind", ind
        #for h in range(len(ind)):
        #    print "h", h
        #    print "ind", ind
        #    element = ind[h]
        #    sl=listOfAngles[element]
            
        #ang.append(sl) #probabilities selecting RIGHT hand = LEFT cortex


    fig4 = plt.figure("Probabilities Per Angle 0 to 360")   
    xx = [h for h in range(len(listOfAngles))]
    plt.subplot(1, 2, 1)
    plt.plot( listOfAngles, probability_right, 'ob')
    plt.subplot(1, 2, 2)
    plt.plot( listOfAngles, probability_left, 'or')
    plt.show()

    # print "angL", len(angL)
    # print "angR", len(angR)

    ax = plt.axes([0.025, 0.025, 0.95, 0.95], polar=True)

    N = len(angL)
    #theta = np.arange(0.0, 2 * np.pi, 2 * np.pi/N)
    theta = angL

    radii = [1 for i in range(N)]
    width = [0.0126 for i in range(N)]
    bars = plt.bar(theta, radii, width=width, bottom=0.0, linewidth=0)

    for r,bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.jet(1000))
        #print probability_right[neu]
        bar.set_alpha(1)
        neu+=1
    
    #ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.show()

    plt.draw()


    ax1 = plt.axes([0.025, 0.025, 0.95, 0.95], polar=True)


    N = len(angR)
    theta = angR

    radii = [1 for i in range(N)]
    width = [0.0126 for i in range(N)]
    bars = plt.bar(theta, radii, width=width, bottom=0.0, linewidth=0)

    for r,bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.jet(r/10.))
        #print probability_right[neu]
        bar.set_alpha(1)
        neu+=1
    
    #ax.set_xticklabels([])
    ax1.set_yticklabels([])

    #plt.show()
    #angle  = listOfAngles
    #print "angle", angle
    #plt.clf()
    #plt.polar(angle, angR, 'or')
    #plt.draw()
    #plt.polar(angle, angL, 'ob')
    plt.draw()

    plt.show()
    
    fig5 = plt.figure("Error Per CORTEX Angle 0 to 360")   
    xx = [h for h in range(len(listOfAngles))]
    plt.subplot(1, 2, 1)
    plt.plot( listOfAngles, error_right, 'ob')
    plt.subplot(1, 2, 2)
    plt.plot( listOfAngles, error_left, 'or')
    plt.show()


    fig6 = plt.figure("Error of selected hand Angle 0 to 360")   
    xx = [h for h in range(len(listOfAngles))]
    plt.subplot(1, 2, 1)
    plt.plot( listOfAngles, error, 'ob')
    plt.show()

if __name__ == "__main__":
	main()