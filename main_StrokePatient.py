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
import collections

trials = 500
energies = [0,0]

def main():

    #ind = int(sys.argv[1])    
    #file_object = open("listInput.txt", "r")
    #lines = file_object.readlines()
    #inputs = lines[ind]
    #file_object.close() 

    #print inputs   
 
    #FORCED_TRIAL = float(inputs[0])
    #GAIN = float(inputs[1])
    #inputS = float(inputs[2])
    FORCED_TRIAL = 0
    GAIN = 0
    STEER = 0

    if(FORCED_TRIAL>0):
        FORCED_TRIAL = FORCED_TRIAL/10
    if(GAIN>0):
        GAIN = GAIN/10
    if(STEER>0):
        STEER = STEER/10

    for snp in range(1):

        if(snp>1):
            STEER = -STEER

        print FORCED_TRIAL
        print GAIN
        print STEER

        f=json.loads(open('Training_v29_model.json').read())

        sensitivityUpdateRight = []
        sensitivityUpdateLeft = []

        nInput = 250

        possibleAngles = [ (i*float(360.00/nInput)) for i in range(nInput)]
        #print "length poss angles", len(possibleAngles), "angles : ", possibleAngles

        N = 500
        leftCortex  = [ Net(math.radians(f['sensitivityUpdateLeft'][i]), "left") for i in range(len(f['sensitivityUpdateLeft']))]
        rightCortex = [ Net(math.radians(f['sensitivityUpdateRight'][i]), "right") for i in range(len(f['sensitivityUpdateRight']))]

        N_extent = 20
        leftCortex_extent  = [ Net(math.radians(i*float(360.00/N_extent)), "left") for i in range(N_extent)]
        rightCortex_extent = [ Net(math.radians(i*float(360.00/N_extent)), "right") for i in range(N_extent)]

        for i in range(N_extent):
            leftCortex_extent[i].weight = (f['weight_extent_L'][i])  # update activity of each cell
            rightCortex_extent[i].weight = (f['weight_extent_R'][i]) # update activity of each cell

        #Generating stroke: we remove  50% of neurons in left cortex -> decrease performance of right hand ----------------------------
        listOfDeadNeurons = []
        listOfDeadNeurons2 = []
        listOfWeights = []

        for i in range(len(leftCortex)):
            listOfWeights.append(math.degrees(leftCortex[i].sensitivity))

            if((leftCortex[i].sensitivity < math.radians(90)) ) :
                listOfDeadNeurons.append(i)

        for i in range(len(listOfDeadNeurons)):
            neuron = listOfDeadNeurons[i]-i
            #GENERATE STROKE NOW !!
            del leftCortex[neuron]

        #print "amount of neurons alive in left cortex after stroke", len(leftCortex)


        listOfWeights = []

        for i in range(len(leftCortex)):
            listOfWeights.append(math.degrees(leftCortex[i].sensitivity))

        #print "listOfWeights AFTER STROKE", listOfWeights

        #print 'sensitivityUpdateLeft', f['sensitivityUpdateLeft']

        #----------------------------------------------------------------------------------------------------------------

        spatialRangeLeft  = (90,270)
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
        actualReward_logs = []


        ######## action choice nets #########
        Nchoice = 10
        pi=math.pi


        #choiceRight= []
        #for i in range(Nchoice):
        #        if (i < Nchoice/2):
        #            centerRBF = (pi+pi/2) + i*pi/Nchoice
        #        else:
        #            centerRBF = i*pi/Nchoice - math.radians(90)
        #        choiceRight.append ( ActionChoiceClass("right", centerRBF, f['weightListCheckRight'][i], 0 ))
                    
        choiceLeft = [ ActionChoiceClass("left", (i*2*pi/Nchoice), f['weightListCheckLeft'][i], 0 ) for i in range(Nchoice)] 
        choiceRight = [ ActionChoiceClass("right", (i*2*pi/Nchoice), f['weightListCheckRight'][i], 0 ) for i in range(Nchoice)] 

        weightListCheckLeft = []
        weightListCheckRight = []

        possibleAngles = [ (i*float(360.00/nInput)) for i in range(nInput)]
        #print "possibleAngles", possibleAngles

        #suffle PossibleAngles
        for x in range(nInput):
            auxShuffle = int ( random.uniform(0,nInput) )
            auxShuffle_2 = possibleAngles[auxShuffle]
            possibleAngles[auxShuffle] = possibleAngles[x]
            possibleAngles[x] = auxShuffle_2


        for e in range(trials):

            print e
            #newdAngle = dAngle
            #r = int(random.uniform(0,500))
            #newdAngle = math.radians(possibleAngles[int(random.uniform(0,nInput) ) ] )
            #newdAngle = math.radians(random.uniform(0,360))
            newdAngle = math.radians(possibleAngles[e%nInput])

            if((e%nInput) == 0 ):
                for x in range(nInput):
                    auxShuffle = int ( random.uniform(0,nInput) )
                    auxShuffle_2 = possibleAngles[auxShuffle]
                    possibleAngles[auxShuffle] = possibleAngles[x]
                    possibleAngles[x] = auxShuffle_2

            #newdAngle = math.radians(30)


            #print "------------------"
            #print "New dAngle ---", math.degrees(newdAngle), " ------->"
            ###########################
            #### direction Conding ####
            ###########################

            a=[ (-0.2+math.cos(newdAngle)), (math.sin(newdAngle))]
            newExtentR = np.linalg.norm(a)
            b=[ (0.2+math.cos(newdAngle) ), (math.sin(newdAngle))]
            newExtentL = np.linalg.norm(b)

            #NewExtentLeft is the actual extent of the optimal movement for the right hand/left cortex
            if ((e>2500) and (e<21000)):
                #fade in gain
                newExtentL = newExtentL - (newExtentL * (GAIN * ( (e-500)/500)) )
            else: 
                if ((e>21000) and (e<23000)):
                    #keep applying gain
                    newExtentL = newExtentL - (newExtentL * GAIN)
                else:
                    
                    if ((e>23000) and (e<23500)):
                        #fade out gain
                        newExtentL = newExtentL - (newExtentL * (GAIN * (1-( (e-3000)/500)) ) )

            startTime = int(round(time.time() * 1000))
            choosenHand = -1;
            acL = 0
            acR = 0

            directionRight, directionLeft, errorListLeft ,errorListRight, allTangSumR, allTangSumL, errorR, errorL, dvL, dvR = directionCodingFunc( leftCortex, rightCortex, newdAngle, N)

            # Extent Right refers to extent coded in right cortex and corresponding to left arm
            extentRight, extentLeft, errorRight_e, errorLeft_e = extentCodingFunc( leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_extent, newdAngle)

            while(choosenHand == -1):
                currT = int(round(time.time() * 1000))

                [energies, angleShoulder, angleElbow] = calculaterEnergies_v1.fComputeEnergies(np.vstack((dvR, dvL))/3., newdAngle, extentRight, extentLeft)
                [choosenHand, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, p_left, p_right, directionLeft_Amp] = returnHandChoice(newdAngle , choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft, 0)
            
                [choosenHand, acL, acR] = CompetingAccumulators(acL, acR, energies, expectedRewardLeft, expectedRewardRight)

                #if ( (e>=500)and(e<1500)):
                #    choosenHand = 1



            #returnHandDict = returnHandChoice(dAngle , choiceLeft , choiceRight)

            #print "---> ", returnHandChoice(dAngle , choiceLeft , choiceRight) , "<---"
            
            #print "rightArm expected reward ", expectedRewardRight
            #print "leftArm expected reward ", expectedRewardLeft
            #print "choosenHand", choosenHand, "-------------"
            #print "extentLeft", extentLeft      
            #print "extentRight", extentRight

            if (e == trials-1):
                for p in range(len(choiceLeft)):
                    weightListCheckLeft.append(choiceLeft[p].weight)
                    weightListCheckRight.append(choiceRight[p].weight)

            #print "WEIGHTS L", weightListCheckLeft
            #print "WEIGHTS R", weightListCheckRight


            #print "indent "
            #### Action value update ###
            
            #print "choosen hand --------> ", choosenHand, "<------------------"

            #if ( (e>=500)and(e<2500)):
            #    choosenHand = 1

            #print "real errorRight_e: ", errorRight_e
            #print "real direction left", math.degrees(directionLeft)

            rt.append(currT - startTime)
            angle_per_trial.append(newdAngle)
            errorLeft_extent.append(errorLeft_e)
            errorRight_extent.append(errorRight_e)
            errorLeft_angle.append(min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs))
            errorRight_angle.append(min(newdAngle-directionRight, newdAngle-directionRight+2*math.pi, newdAngle-directionRight-2*math.pi, key=abs))
            expected_L.append(expectedRewardLeft)
            expected_R.append(expectedRewardRight)


            if ((e>2500) and (e<23500)):
                #choosenHand=1
                errorAngle = min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs)
                
                STEER_help = STEER

                if ((e>2500) and (e<21000)):
                    #fade in steer
                    STEER_help = STEER * (e-500)/500
                else:
                    if ( (e>23000) and (e<23500) ):
                        #fade out steer
                        STEER_help = STEER - (STEER * (e-3000) /500 )

                directionLeft = directionLeft + (errorAngle * STEER_help)

                if(directionLeft>=(2*math.pi)):
                    directionLeft = directionLeft - (2*math.pi)
                else:
                    if(directionLeft<0):
                        directionLeft = directionLeft + (2*math.pi)

                if(random.uniform(0,1) < FORCED_TRIAL):
                    choosenHand = 1;
                #print "manip errorRight_e: ", errorRight_e
                #print "manip directionLeft: ", math.degrees(directionLeft)
                #print "energiesL", energies[1]
                #print "energiesR", energies[0]

            
            choosen_per_trial.append(choosenHand)


            if(choosenHand==0):
                actualReward = math.exp( -(( min(newdAngle-directionRight, newdAngle-directionRight+2*math.pi, newdAngle-directionRight-2*math.pi, key=abs) **2) / 0.2**2)) - (math.sqrt(errorRight_e**2))
            else:
                actualReward = math.exp( -(( min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs) **2) / 0.2**2)) - (math.sqrt(errorLeft_e**2))

            #predictionErrorL = (actualReward-(errorLeft_e*0.2) - energies[1]*20)-expectedRewardLeft
            #predictionErrorR = (actualReward-(errorRight_e*0.2) - energies[0]*20)- expectedRewardRight
            predictionErrorL = actualReward - expectedRewardLeft
            predictionErrorR = actualReward - expectedRewardRight

            actualReward_logs.append(actualReward)


            #print "trial : ", e

            if(choosenHand==1):

                #print "actual reward", actualReward
                #print "actual reward nonUsed", actualReward_nonUsed

                #print "leftArm.actionValue", leftArm.actionValue
                #print "rightArm.actionValue", rightArm.actionValue

                # cortex left
                for i in range(len(choiceLeft)):
                    #choiceLeft[i].weight += 0.1* leftArm.actionValue * math.exp( -((math.radians(newdAngle))  - math.radians(choiceLeft[i].center) )**2 / (math.pi/10))
                    #choiceLeft[i].weight  += 0.1* leftArm.actionValue * math.exp( -((math.radians(newdAngle))  - math.radians(choiceLeft[i].center) )**2 / (math.pi/10)**2)
                    #choiceLeft[i].weight  += 0.1 * predictionErrorL * math.exp( -  ( (min(newdAngle-choiceLeft[i].center, newdAngle-choiceLeft[i].center+2*math.pi, newdAngle-choiceLeft[i].center-2*math.pi, key=abs)**2) / (math.pi/10.0)**2) ) 
                    choiceRight[i].weight  += 0.1 * predictionErrorR * math.exp( -  (  ( min(newdAngle-choiceRight[i].center, newdAngle-choiceRight[i].center+2*math.pi, newdAngle-choiceRight[i].center-2*math.pi, key=abs))**2 / (math.pi/10)**2) )

            if(choosenHand==0):

                #print "actual reward", actualReward
                #print "actual reward nonUsed", actualReward_nonUsed


                # cortex right
                for i in range(len(choiceRight)):
                    choiceLeft[i].weight  += 0.1 * predictionErrorL * math.exp( -  ( (min(newdAngle-choiceLeft[i].center, newdAngle-choiceLeft[i].center+2*math.pi, newdAngle-choiceLeft[i].center-2*math.pi, key=abs))**2 / (math.pi/10)**2) )
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
                    sensitivityUpdateLeft.append(math.degrees(leftCortex[i].learningRuleFunc( directionLeft, newdAngle)))
                #leftCortex[i].activity = 0 #reset activity of the neuron for next trial
                for i in range(len(leftCortex_extent)):
                    leftCortex_extent[i].learningRuleFunc_extent( errorLeft_e)

                #print " sum acts LEFT ", sumOfSquareActivitiesLeft
                sumOfSquareActivitiesListLeft.append(sumOfSquareActivitiesLeft)


            if(choosenHand==0):
            #if(True):
                sensitivityUpdateRight = []
                sumOfSquareActivitiesRight = 0
        
                for i in range(len(rightCortex)):
                    sumOfSquareActivitiesRight += rightCortex[i].activity
                    sensitivityUpdateRight.append(math.degrees(rightCortex[i].learningRuleFunc( directionRight, newdAngle)))
                    #   rightCortex[i].activity = 0 #reset activity of the neuron for next trial
                
                for i in range(len(rightCortex_extent)):
                    rightCortex_extent[i].learningRuleFunc_extent( errorRight_e )
       
                #print "sum acts RIGHT ", sumOfSquareActivitiesRight
                sumOfSquareActivitiesListRight.append(sumOfSquareActivitiesRight)
                    #if(e>1995):
                        #print "R Weights"
                        #print choiceRight[i].weight
                        #print "L Weights"
                        #print choiceLeft[i].weight

            #print "-------------------------------------"


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

        #for i in range(nInput):
        #    angle = math.radians(possibleAngles[i])
        #    newExtentL = math.sqrt( ((-0.2+math.cos(angle))**2) + (math.sin(angle)**2) )
        #    newExtentR = math.sqrt( ((0.2+math.cos(angle))**2) + (math.sin(angle)**2) )
        #    directionRight, directionLeft, errorListLeft ,errorListRight, b, c, errorR, errorL, dvL, dvR = directionCodingFunc( leftCortex, rightCortex, angle, N)
        #    [choosenHand, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, p_left, p_right, directionLeft_Amp] = returnHandChoice(angle, choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft, 0)
        #    probability_right.append(p_right)        
        #    probability_left.append(p_left)
        #    error_right.append(errorR)
        #    error_left.append(errorL)
        #    extentRight, extentLeft, errorRight_e, errorLeft_e = extentCodingFunc( leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_extent, newdAngle)
        #    error_extent_right.append(errorRight_e)
        #    error_extent_left.append(errorLeft_e)
        #    if (p_right > p_left):
        #        error.append(errorR)
        #    else:
        #        error.append(errorL)

        #print "possAngles", possibleAngles

        #print "weightsR", weightListCheckRight
        #print "weightsL", weightListCheckLeft
        #print "sensitivityUpdateLeft", sensitivityUpdateLeft
        #print "sensitivityUpdateRight", sensitivityUpdateRight


        #y=collections.Counter(listOfAngles)
        #listRepetitions = [i for i in y if y[i]>1]
        #print "Angles repeated : ", len(listRepetitions)



        #for j in range(nInput):
        #    sl=0
        #    sr=0
        #    ind = [i for i,val in enumerate(listOfAngles) if val==j]
        #    for h in range(len(ind)):
        #        print "h", h
        #        print "ind", ind
        #        element = ind[h]
        #        sl=probability_left[element]
        #        sr=probability_right[element]
        #        
        #    meanProbRight.append(sl) #probabilities selecting RIGHT hand = LEFT cortex
        #    meanProbLeft.append(sr) 


        sensitivityLeft = []
        sensitivityRight = []
        for j in range(len(rightCortex)):
            sensitivityRight.append(math.degrees(rightCortex[j].sensitivity) )
        for j in range(len(leftCortex)):
            sensitivityLeft.append (math.degrees(leftCortex[j].sensitivity) )

        for j in range(N_extent):
            weight_extent_Left.append(leftCortex_extent[j].weight)
            weight_extent_Right.append(rightCortex_extent[j].weight)

        dictModel = { 'weightListCheckLeft' : weightListCheckLeft, 'weightListCheckRight' : weightListCheckRight, 'sensitivityUpdateLeft':sensitivityLeft , 'sensitivityUpdateRight' : sensitivityRight, 'weight_extent_R': weight_extent_Right, 'weight_extent_L': weight_extent_Left, "error_extent_right": error_extent_right, "error_extent_left": error_extent_left, "error_right": error_right, "error_left": error_left}

        #with open('dataStroke_v8_model_%i%i%i%i.json'%(inputT,inputG,inputS,snp), 'wb') as f:
        with open('datanoStroke_v9_model.json', 'wb') as f:
   
            #save training weights to file
            json.dump(dictModel,f)


        dictLogs = { 'Choosen' : choosen_per_trial, 'angle_per_trial' : angle_per_trial, 'rt' : rt, 'errorLeft_extent':errorLeft_extent, 'errorRight_extent':errorRight_extent,  'errorLeft_angle':errorLeft_angle, 'errorRight_angle':errorRight_angle, 'expected_L':expected_L, 'expected_R': expected_R, 'actualReward_logs':actualReward_logs}


        #with open('dataStroke_v8_Logs_%i%i%i%i.json'%(inputT,inputG,inputS,snp), 'wb') as file:
        with open('datanoStroke_v9_Logs.json', 'wb') as file:
            #save training weights to file
            json.dump(dictLogs,file)


        dictWeights = { 'meanProbRight' : probability_right, 'meanProbLeft' : probability_left, 'listOfAngles' : listOfAngles}

        #with open('dataStroke_v8_%i%i%i%i.json'%(inputT,inputG,inputS,snp), 'wb') as file:
        with open('datanoStroke_v9.json', 'wb') as file:
            #save training weights to file
            json.dump(dictWeights,file)

    #print "length left",    len(probability_left)
    #print "length right", len(probability_right)
    #print "length list of angles", len(listOfAngles), " angles : ", listOfAngles


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
    
    '''
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
    """
    
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
    plt.plot( listOfAngles, probability_right, 'ob')
    plt.subplot(1, 2, 2)
    plt.plot( listOfAngles, probability_left, 'or')
    plt.show()
    """

    #plt.pie(meanProbLeft)

   















    ## -------------- PLOTS ----------------------------------

    fileStroke=json.loads(open('dataStroke_v4_lessGain.json').read())
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

    print len(probability_right)
    """
    neu = 0
    
    angL = []
    angR = []


    print "probability_right", probability_right
    print "probability_left", probability_left

    print "listOfAngles", listOfAngles


    for i in range(nInput):
        if (probability_left[i]>0.5):
            angL.append(listOfAngles[i])

        else:
            if(probability_right[i]>=0.5):
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

    print "angL", len(angL)
    print "angR", len(angR)

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
    '''
    

if __name__ == "__main__":
	main()