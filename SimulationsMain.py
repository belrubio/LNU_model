import numpy as np
import pprint, random, time
import matplotlib.pyplot as plt
from motorCortexNet import *
from actionChoiceNet import *
from choice import *
from armReward import *
from directionCoding import * 
import json
import calculaterEnergies_v1
import fakeTabs_v2

doPlot=0
trials = 35
handSelected = -1
energies = [0, 0]
expectedRewardRight = 0
expectedRewardLeft = 0

def SimulationsMain(UI, in_UDLR, in_EBLR, in_RBLR, in_EL, in_RD, in_trials, in_showTrial1, in_showTrial2, simulateStroke, simulateRehab, simulateFU, FORCED_TRIAL, GAIN, STEER):

    global energies
    global expectedRewardLeft
    global expectedRewardRight

    trials = in_trials 
    Exploration_Level = in_EL
    ErrorBasedLearning = in_EBLR
    UseDependentLearning = in_UDLR
    ReinforcementBasedLearning = in_RBLR

    energies = [0, 0]
    sensitivityUpdateRight = []
    sensitivityUpdateLeft = []
    N = 500 
    N_extent = 20
    Nchoice = 10
    pi=math.pi
    leftCortex_extent  = [ Net(math.radians(i*float(360.00/N_extent)), "left") for i in range(N_extent)]
    rightCortex_extent = [ Net(math.radians(i*float(360.00/N_extent)), "right") for i in range(N_extent)]

    if (simulateStroke):
        print ("We are simulating a Stroke!")
        f=json.loads(open('Trainned_model.json').read())
        leftCortex  = [ Net(math.radians(f['sensitivityUpdateLeft'][i]), "left") for i in range(len(f['sensitivityUpdateLeft']))]
        rightCortex = [ Net(math.radians(f['sensitivityUpdateRight'][i]), "right") for i in range(len(f['sensitivityUpdateRight']))]

        for i in range(N_extent):
            leftCortex_extent[i].weight = (f['weight_extent_L'][i])  # update activity of each cell
            rightCortex_extent[i].weight = (f['weight_extent_R'][i]) # update activity of each cell

        #Generating stroke: we remove  50% of neurons in left cortex -> decrease performance of right hand ----------------------------
        listOfDeadNeurons = []
        listOfDeadNeurons2 = []
        

        for i in range(len(leftCortex)):
            #listOfWeights.append(math.degrees(leftCortex[i].sensitivity))

            if((leftCortex[i].sensitivity < math.radians(90)) ) :
                listOfDeadNeurons.append(i)

        for i in range(len(listOfDeadNeurons)):
            neuron = listOfDeadNeurons[i]-i
            #GENERATE STROKE NOW !!
            del leftCortex[neuron]

        choiceLeft = [ ActionChoiceClass("left", (i*2*pi/Nchoice), f['weightListCheckLeft'][i], 0 ) for i in range(Nchoice)] 
        choiceRight = [ ActionChoiceClass("right", (i*2*pi/Nchoice), f['weightListCheckRight'][i], 0 ) for i in range(Nchoice)] 

    else:

        if(simulateRehab or simulateFU):
           
            f=json.loads(open('Trainned_model_stroke.json').read())
            leftCortex  = [ Net(math.radians(f['sensitivityUpdateLeft'][i]), "left") for i in range(len(f['sensitivityUpdateLeft']))]
            rightCortex = [ Net(math.radians(f['sensitivityUpdateRight'][i]), "right") for i in range(len(f['sensitivityUpdateRight']))]

            for i in range(N_extent):
                leftCortex_extent[i].weight = (f['weight_extent_L'][i])  # update activity of each cell
                rightCortex_extent[i].weight = (f['weight_extent_R'][i]) # update activity of each cell

            choiceLeft = [ ActionChoiceClass("left", (i*2*pi/Nchoice), f['weightListCheckLeft'][i], 0 ) for i in range(Nchoice)] 
            choiceRight = [ ActionChoiceClass("right", (i*2*pi/Nchoice), f['weightListCheckRight'][i], 0 ) for i in range(Nchoice)] 

        else:

            
            leftCortex  = [ Net(math.radians(i*float(360.00/N)), "left") for i in range(N)]
            rightCortex = [ Net(math.radians(i*float(360.00/N)), "right") for i in range(N)]

            for i in range(N_extent):
                leftCortex_extent[i].weight = 0.3 # update activity of each cell
                rightCortex_extent[i].weight = 0.3 # update activity of each cell

            #weights should be initialized to...
            choiceLeft = [ ActionChoiceClass("left", (i*2*pi/Nchoice),0.5,0) for i in range(Nchoice)]
            choiceRight= [ ActionChoiceClass("right", (i*2*pi/Nchoice),0.5,0) for i in range(Nchoice)]


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

    weightListCheckLeft = []
    weightListCheckRight = []

    nInput = 250 # FREEPARAM

    possibleAngles = [ (i*float(360.00/nInput)) for i in range(nInput)]

    #suffle PissibleAnles
    for x in range(nInput):
        auxShuffle = int ( random.uniform(0,nInput) )
        auxShuffle_2 = possibleAngles[auxShuffle]
        possibleAngles[auxShuffle] = possibleAngles[x]
        possibleAngles[x] = auxShuffle_2

    for e in range(trials):

        UI.progressbar["maximum"] = trials
        UI.progressbar["value"] = e
        UI.style.configure('text.Horizontal.TProgressbar', 
                    text='{:g}'.format(e))  # update label
        UI.progressbar.update()
        newdAngle = math.radians(possibleAngles[e%nInput])

        if((e%nInput) == 0 ):
            for x in range(nInput):
                auxShuffle = int ( random.uniform(0,nInput) )
                auxShuffle_2 = possibleAngles[auxShuffle]
                possibleAngles[auxShuffle] = possibleAngles[x]
                possibleAngles[x] = auxShuffle_2
        
    	###########################
    	#### direction Conding ####
    	###########################
        a=[ (-0.2+math.cos(newdAngle)), (math.sin(newdAngle))]
        newExtentR = np.linalg.norm(a)
        b=[ (0.2+math.cos(newdAngle) ), (math.sin(newdAngle))]
        newExtentL = np.linalg.norm(b)

        #NewExtentLeft is the actual extent of the optimal movement for the right hand/left cortex
        if (simulateRehab):
            #keep applying gain
            newExtentL = newExtentL - (newExtentL * GAIN)
                
        startTime = int(round(time.time() * 1000))
        choosenHand = -1
        handSelected = -1
        acL = 0
        acR = 0
        pacL = 0
        pacR = 0
        ac = 0

        #print "newExtentL : ", newExtentL
        #print "newExtentR : ", newExtentR

        directionRight, directionLeft, errorListLeft ,errorListRight, allTangSumR, allTangSumL, errorR, errorL, dvL, dvR = directionCodingFunc( leftCortex, rightCortex, newdAngle, N)

        extentRight, extentLeft, errorRight_e, errorLeft_e = extentCodingFunc( leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_extent, newdAngle)

        while(choosenHand == -1):
            currT = int(round(time.time() * 1000))

            [energies, angleShoulder, angleElbow] = calculaterEnergies_v1.fComputeEnergies(np.vstack((dvR, dvL))/3., newdAngle, extentRight, extentLeft)
            [choosenH, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, p_left, p_right, directionLeft_Amp] = returnHandChoice(newdAngle , choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft, 0, Exploration_Level)
            
            #Show 5 consecutive trials
            if (e>=in_showTrial1 and e<in_showTrial1+6) or (e>=in_showTrial2 and e<in_showTrial2+6):
                ac, pacR, pacL = UI.play_trial(angleShoulder[choosenHand], angleElbow[choosenHand], np.cos(newdAngle)/(np.sqrt(np.cos(newdAngle)**2+np.sin(newdAngle)**2))/3., np.sin(newdAngle)/(np.sqrt(np.cos(newdAngle)**2+np.sin(newdAngle)**2))/3.+0.4, choosenHand, acR, acL, pacR, pacL, ac, expectedRewardRight, expectedRewardLeft, startTime, currT, e, False)
            
            [choosenHand, acL, acR] = CompetingAccumulators(acL, acR, energies, expectedRewardLeft, expectedRewardRight)
            #print "choosenHand in : ", angleShoulder, "-------------"

        # print("angle"+ str(math.degrees(newdAngle)))
        # print("angleShoulder")
        # print(angleShoulder)
        # print("angleElbow")
        # print(angleElbow)

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

        if (simulateRehab):
            errorAngle = min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs)
            STEER_help = STEER
            directionLeft = directionLeft + (errorAngle * STEER_help)

            if(directionLeft>=(2*math.pi)):
                directionLeft = directionLeft - (2*math.pi)
            else:
                if(directionLeft<0):
                    directionLeft = directionLeft + (2*math.pi)

            if(random.uniform(0,1) < FORCED_TRIAL):
                choosenHand = 1;


        if (e>=in_showTrial1 and e<in_showTrial1+6) or (e>=in_showTrial2 and e<in_showTrial2+6):
            for step in range(len(angleShoulder)):
                ac, pacR, pacL = UI.play_trial(angleShoulder[step, choosenHand], angleElbow[step, choosenHand], np.cos(newdAngle)/(np.sqrt(np.cos(newdAngle)**2+np.sin(newdAngle)**2))/3., np.sin(newdAngle)/(np.sqrt(np.cos(newdAngle)**2+np.sin(newdAngle)**2))/3.+0.4, choosenHand, acR, acL, pacR, pacL, ac, expectedRewardRight, expectedRewardLeft, startTime, currT, e, True)


        if (e == trials-1):
            for p in range(len(choiceLeft)):
                weightListCheckLeft.append(choiceLeft[p].weight)
                weightListCheckRight.append(choiceRight[p].weight)

        if(choosenHand==0):
            actualReward = math.exp( -(( min(newdAngle-directionRight, newdAngle-directionRight+2*math.pi, newdAngle-directionRight-2*math.pi, key=abs) **2) / 0.2**2)) - (math.sqrt(errorRight_e**2)*0.1)
        else:
            actualReward = math.exp( -(( min(newdAngle-directionLeft, newdAngle-directionLeft+2*math.pi, newdAngle-directionLeft-2*math.pi, key=abs) **2) / 0.2**2)) - (math.sqrt(errorLeft_e**2)*0.1)

        actualReward_logs.append(actualReward)
    
        predictionErrorL = actualReward - expectedRewardLeft
        predictionErrorR = actualReward - expectedRewardRight

    
        if(choosenHand==1):
        
            # cortex left
            for i in range(len(choiceRight)):
                choiceRight[i].weight  += ReinforcementBasedLearning * predictionErrorR * math.exp( -  (  ( min(newdAngle-choiceRight[i].center, newdAngle-choiceRight[i].center+2*math.pi, newdAngle-choiceRight[i].center-2*math.pi, key=abs))**2 / (math.pi/10)**2) )
                # FREEPARAM


        if(choosenHand==0):

            # cortex right
            for i in range(len(choiceRight)):
                choiceLeft[i].weight  += ReinforcementBasedLearning * predictionErrorL * math.exp( -  (  ( min(newdAngle-choiceLeft[i].center, newdAngle-choiceLeft[i].center+2*math.pi, newdAngle-choiceLeft[i].center-2*math.pi, key=abs))**2 / (math.pi/10)**2) )

        if(choosenHand==1):

            sensitivityUpdateLeft = []
            sumOfSquareActivitiesLeft = 0
            for i in range(len(leftCortex)):
                sumOfSquareActivitiesLeft += leftCortex[i].activity
                sensitivityUpdateLeft.append(math.degrees(leftCortex[i].learningRuleFunc(directionLeft, newdAngle, ErrorBasedLearning, UseDependentLearning)))
            for i in range(len(leftCortex_extent)):
                leftCortex_extent[i].learningRuleFunc_extent( errorLeft_e)
                
            #print " sum acts LEFT ", sumOfSquareActivitiesLeft
            sumOfSquareActivitiesListLeft.append(sumOfSquareActivitiesLeft)


        if(choosenHand==0):

            sensitivityUpdateRight = []
            sumOfSquareActivitiesRight = 0
    
            for i in range(len(rightCortex)):
                sumOfSquareActivitiesRight += rightCortex[i].activity
                sensitivityUpdateRight.append(math.degrees(rightCortex[i].learningRuleFunc( directionRight, newdAngle, ErrorBasedLearning, UseDependentLearning)))
            for i in range(len(rightCortex_extent)):
                rightCortex_extent[i].learningRuleFunc_extent( errorRight_e )
    
            sumOfSquareActivitiesListRight.append(sumOfSquareActivitiesRight)

    UI.style.configure('text.Horizontal.TProgressbar', 
                    text='{:g}'.format(trials))  # update label
    UI.progressbar["value"] = trials
    UI.progressbar.update()

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
    expectedRewardR = []
    expectedRewardL = []
    energy_L=[]
    energy_R=[]

    possibleAngles = np.arange(0,360,360/500.)

    for i in range(len(possibleAngles)):
        angle = math.radians(possibleAngles[i])
        #newExtentL = math.sqrt( ((-0.3+math.cos(angle))**2) + (math.sin(angle)**2) )
        #newExtentR = math.sqrt( ((0.3+math.cos(angle))**2) + (math.sin(angle)**2) )
        a=[ (-0.2+math.cos(angle)), (math.sin(angle))]
        newExtentR = np.linalg.norm(a)
        b=[ (0.2+math.cos(angle) ), (math.sin(angle))]
        newExtentL = np.linalg.norm(b)
        directionRight, directionLeft, errorListLeft ,errorListRight, b, c, errorR, errorL, dvL, dvR = directionCodingFunc( leftCortex, rightCortex, angle, N)
        [choosenHand, actualReward, actualReward_nonUsed, expectedRewardLeft, expectedRewardRight, p_left, p_right, directionLeft_Amp] = returnHandChoice(angle, choiceLeft , choiceRight, leftArm, rightArm, directionRight, directionLeft, 0, Exploration_Level)
        probability_right.append(p_right)        
        probability_left.append(p_left)
        error_right.append(errorR)
        error_left.append(errorL)
        expectedRewardL.append(expectedRewardLeft)
        expectedRewardR.append(expectedRewardRight)
        extentRight, extentLeft, errorRight_e, errorLeft_e = extentCodingFunc( leftCortex_extent, rightCortex_extent, newExtentL, newExtentR , N_extent, newdAngle)
        error_extent_right.append(errorRight_e)
        error_extent_left.append(errorLeft_e)
        if (p_right > p_left):
            error.append(errorR)
        else:
            error.append(errorL)

        [energies, angleShoulder, angleElbow] = calculaterEnergies_v1.fComputeEnergies(np.vstack((dvR, dvL))/3., angle, extentRight, extentLeft)
        energy_L.append(energies[1])
        energy_R.append(energies[0])

    sensitivityLeft = []
    sensitivityRight = []
    for j in range(len(rightCortex)):
        sensitivityRight.append(math.degrees(rightCortex[j].sensitivity) )
    for j in range(len(leftCortex)):
        sensitivityLeft.append (math.degrees(leftCortex[j].sensitivity) )

    #print("sensitivityLeft length " + str(len(sensitivityLeft)))

    for j in range(N_extent):
        weight_extent_Left.append(leftCortex_extent[j].weight)
        weight_extent_Right.append(rightCortex_extent[j].weight)

    UI.drawTrialData(e, rt, angle_per_trial, possibleAngles, probability_right, probability_left, error_right, error_left, errorRight_e, errorLeft_e, expectedRewardR, expectedRewardL, energy_R, energy_L, sensitivityRight, sensitivityLeft)

    meanProbLeft = []
    meanProbRight = []

    dictWeights = { 'weightListCheckLeft' : weightListCheckLeft, 'weightListCheckRight' : weightListCheckRight, 'sensitivityUpdateLeft':sensitivityLeft , 'sensitivityUpdateRight' : sensitivityRight, 'weight_extent_R': weight_extent_Right, 'weight_extent_L': weight_extent_Left, "error_extent_right": error_extent_right, "error_extent_left": error_extent_left, "error_right": error_right, "error_left": error_left}


    if(simulateStroke or simulateRehab):
        with open('Trainned_model_stroke.json', 'w') as f:
            #save training weights to file
            json.dump(dictWeights,f)
    else:
        if(simulateFU):
            with open('Trainned_model_rehab.json', 'w') as f:
                #save training weights to file
                json.dump(dictWeights,f)
        else:
            with open('Trainned_model.json', 'w') as f:
                #save training weights to file
                json.dump(dictWeights,f)

    dictWeights = { 'meanProbRight' : probability_right, 'meanProbLeft' : probability_left, 'listOfAngles' : listOfAngles}
    with open('Trainned_probabilities.json', 'w') as file:
        #save training weights to file
        json.dump(dictWeights,file)

    dictLogs = { 'Choosen' : choosen_per_trial, 'angle_per_trial' : angle_per_trial, 'rt' : rt, 'errorLeft_extent':errorLeft_extent, 'errorRight_extent':errorRight_extent,  'errorLeft_angle':errorLeft_angle, 'errorRight_angle':errorRight_angle, 'expected_L':expected_L, 'expected_R': expected_R, 'energy_L': energy_L, 'energy_R': energy_R, 'actualReward_logs':actualReward_logs}
    with open('Trainned_logs.json', 'w') as file:
        #save training weights to file
        json.dump(dictLogs,file)

    print("files saved")
    

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
    

    # fig20 = plt.figure("sensitivityUpdateLeft")   
    # xx = [h for h in range(len(sensitivityLeft))]
    # plt.plot( xx, sensitivityUpdateLeft)
    # fig20.canvas.draw()
    # #plt.show()
       
    # fig2 = plt.figure("sensitivityUpdateRight")   
    # xx = [h for h in range(len(sensitivityRight))]
    # plt.plot( xx, sensitivityUpdateRight)
    # fig2.canvas.draw()
    # plt.show()
    


    # #print "Sensitivities Right length ", len(sensitivityUpdateRight), " val  ",  sensitivityUpdateRight
    # #print "Sensitivities Left length ", len(sensitivityUpdateLeft), "  val ", sensitivityUpdateLeft


    # fig3 = plt.figure("weightListCheckRight=red")   
    # xx = [h for h in range(len(weightListCheckRight))]
    # plt.plot( xx, weightListCheckRight, '-or')
    # fig3.canvas.draw()
    # plt.plot( xx, weightListCheckLeft, '-ob')
    # fig3.canvas.draw()
    # plt.show()

    # fig4 = plt.figure("weights EXTENT.Right=red")   
    # xx = [h for h in range(len(weight_extent_Right))]
    # plt.plot( xx, weight_extent_Right, '-or')
    # fig3.canvas.draw()
    # plt.plot( xx, weight_extent_Left, '-ob')
    # fig3.canvas.draw()
    # plt.show()





    # ## -------------- PLOTS ----------------------------------

    # fileStroke=json.loads(open('Training_v29_probability.json').read())
    # probability_right = []
    # probability_left = []
    # listOfAngles = []

    # for i in range(nInput):
    #     #    print fileStroke['meanProbRight'][i]
    #     #    print i
    #     probability_right.append(fileStroke['meanProbRight'][i])
    #     probability_left.append(fileStroke['meanProbLeft'][i])
    #     listOfAngles.append( math.radians(possibleAngles[i]) )


    #     #probability_left.append(fileStroke['meanProbLeft'][i])


    

    # """
    # for i in range(500):
    #     for j in range(500):
    #         if (listOfAngles[i]>listOfAngles[j]):
    #             aux=listOfAngles[i]
    #             listOfAngles[i] = listOfAngles[j]
    #             listOfAngles[j] = aux

    #             aux=probability_left[i]
    #             probability_left[i] = probability_left[j]
    #             probability_left[j] = aux

    #             aux=probability_right[i]
    #             probability_right[i] = probability_right[j]
    #             probability_right[j] = aux
    # """
    
    
    # #print len(probability_right)
    # #print len(probability_left)

    # neu = 0

    # angL = []
    # angR = []

    # #print "probability_right", probability_right
    # #print "probability_left", probability_left

    # #print "listOfAngles", listOfAngles

    # for i in range(nInput):
    #     if (probability_left[i]>0.5):
    #         angL.append(listOfAngles[i])

    #     else:
    #         #if (probability_left[i]==0.5):
    #         #    angL.append(listOfAngles[i])
    #         #    angR.append(listOfAngles[i])

    #         if(probability_right[i]>0.5):
    #             angR.append(listOfAngles[i])


    #     #print "ind", ind
    #     #for h in range(len(ind)):
    #     #    print "h", h
    #     #    print "ind", ind
    #     #    element = ind[h]
    #     #    sl=listOfAngles[element]
            
    #     #ang.append(sl) #probabilities selecting RIGHT hand = LEFT cortex

       
    # if (doPlot==1):

    #     fig4 = plt.figure("Probabilities Per Angle 0 to 360")   
    #     xx = [h for h in range(len(listOfAngles))]
    #     plt.subplot(1, 2, 1)
    #     plt.plot( listOfAngles, probability_right, 'ob')
    #     plt.subplot(1, 2, 2)
    #     plt.plot( listOfAngles, probability_left, 'or')

    #     fig4 = plt.figure("Probabilities Per Angle 0 to 360")   
    #     xx = [h for h in range(len(listOfAngles))]
    #     plt.subplot(1, 2, 1)
    #     plt.plot( listOfAngles, probability_right, 'ob')
    #     plt.subplot(1, 2, 2)
    #     plt.plot( listOfAngles, probability_left, 'or')
    #     plt.show()

    #     ax = plt.axes([0.025, 0.025, 0.95, 0.95], polar=True)
    #     N = len(angL)
    #     theta = angL
    #     radii = [1 for i in range(N)]
    #     width = [0.0126 for i in range(N)]
    #     bars = plt.bar(theta, radii, width=width, bottom=0.0, linewidth=0)

    #     for r,bar in zip(radii, bars):
    #         bar.set_facecolor(plt.cm.jet(1000))
    #         bar.set_alpha(1)
    #         neu+=1
        
    #     ax.set_yticklabels([])
    #     plt.show()
    #     plt.draw()

    #     ax1 = plt.axes([0.025, 0.025, 0.95, 0.95], polar=True)
    #     N = len(angR)
    #     theta = angR
    #     radii = [1 for i in range(N)]
    #     width = [0.0126 for i in range(N)]
    #     bars = plt.bar(theta, radii, width=width, bottom=0.0, linewidth=0)
    #     for r,bar in zip(radii, bars):
    #         bar.set_facecolor(plt.cm.jet(r/10.))
    #         bar.set_alpha(1)
    #         neu+=1
    #     ax1.set_yticklabels([])
    #     plt.draw()
    #     plt.show()
        
    #     fig5 = plt.figure("Error Per CORTEX Angle 0 to 360")   
    #     xx = [h for h in range(len(listOfAngles))]
    #     plt.subplot(1, 2, 1)
    #     plt.plot( listOfAngles, error_right, 'ob')
    #     plt.subplot(1, 2, 2)
    #     plt.plot( listOfAngles, error_left, 'or')
    #     plt.show()

    #     fig6 = plt.figure("Error of selected hand Angle 0 to 360")   
    #     xx = [h for h in range(len(listOfAngles))]
    #     plt.subplot(1, 2, 1)
    #     plt.plot( listOfAngles, error, 'ob')
    #     plt.show()

    return True

# if __name__ == "__main__":
# 	main()