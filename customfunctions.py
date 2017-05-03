# -*- coding: utf-8 -*-
from deap import tools, base, creator, algorithms
import random
import matplotlib.pyplot as plt
rewards = [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000]


#evaluate score maximizing financial gains and minimizing missed oppotunities
def evaluate(member):
    rewards = 0
    rewards = member[1][0]
    missedOpps = member[1][1]
    return rewards, missedOpps

def resetScores(population):
    for member in population:
        member[1][0] = 0
        member[1][1] = 0

def initializeNonUniform(initializedOptions):
    return random.choice(initializedOptions)

#offersLeft number between 0 and 8 in decimal
#roundNumber is what index in the rewards list they're in (0, 1, 2, ... ,7 )
#member is the member of the population (list of lists)
def makeDecisionConditional(offersLeft, roundNumber, member):
    decision = 0

    #offer stored in rewards
    offer = rewards[roundNumber]
    #print "offer:\t" + str(offer)

    #roundBin = int(str(roundNumber), 2)
    roundBin = format(roundNumber, 'b').zfill(3)
    #offersLeftBin = int(str(offersLeft), 2)
    offersLeftBin = format(offersLeft, 'b').zfill(3)

    decision_spot = roundBin + offersLeftBin

    decision_spot = int(decision_spot, 2)

    decision_bit = member[0][decision_spot]
    #print "decision bit:\t" + str(decision_bit)

    if offersLeft > 0 and decision_bit == 0:
        decision = 0
    elif offersLeft > 0 and decision_bit == 1:
        if offersLeft < 3:
            decision = 1
            offersLeft -= 1
            member[1][0] += offer
    elif offersLeft > 0 and decision_bit == 2:
        if offersLeft < 2:
            decision = 1
            offersLeft -= 1
            member[1][0] += offer
    elif offersLeft > 0 and decision_bit == 3:
        decision = 1
        offersLeft -= 1
        member[1][0] += offer
    elif offersLeft == 0 and decision_bit != 0:
        member[1][1] += 1 #missed opportunity increment
        decision = 0


    #print "Offers left: \t" + str(offersLeft)
    return [decision, offersLeft]


def makeDecisionBinary(offersLeft, roundNumber, member):
    decision = 0

    #offer stored in rewards
    offer = rewards[roundNumber]
    #print "offer:\t" + str(offer)

    #roundBin = int(str(roundNumber), 2)
    roundBin = format(roundNumber, 'b').zfill(3)
    #offersLeftBin = int(str(offersLeft), 2)
    offersLeftBin = format(offersLeft, 'b').zfill(3)

    decision_spot = roundBin + offersLeftBin

    decision_spot = int(decision_spot, 2)

    decision_bit = member[0][decision_spot]
    #print "decision bit:\t" + str(decision_bit)

    if offersLeft > 0 and decision_bit == 0:
        decision = 0
    elif offersLeft == 0 and decision_bit != 0:
        member[1][1] += 1 #missed opportunity increment
        decision = 0
    elif offersLeft > 0 and decision_bit == 1:
        decision = 1
        member[1][0] += offer
        offersLeft -= 1

    #print "Offers left: \t" + str(offersLeft)
    return [decision, offersLeft]




def mutateFlipBit(individual, indpb=0.1, indpb2 = 0.0):
    decisionSlice = individual[0][8:]
    genome = (individual[0][0:8])
    genome = (list)(tools.mutFlipBit(genome, indpb))

    fullGen =  genome[0] + (decisionSlice)
    individual[0] = fullGen
    #individual[0] = individual[0].pop(0)
    testvar = random.random
    if testvar < indpb2:
        individual[5] = random.randint(0,3)
    return individual, #comma here


def pareto_frontier(Xs, Ys, maxX = True, maxY = True):
    # Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:
                p_front.append(pair)
        else:
            if pair[1] <= p_front[-1][1]: # Look for lower values of Y…
                p_front.append(pair) # … and add them to the Pareto frontier
    # Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY

def graphObjectives(population):
    xs = []
    ys = []
    for member in population:
        xs.append(member[1][0])
        ys.append(member[1][1])

    p_front = pareto_frontier(xs, ys, maxX = True, maxY = False)

    plt.scatter(xs, ys)
    plt.plot(p_front[0], p_front[1])
    plt.ylabel('# opportunities missed')
    plt.xlabel('$ rewards taken')
    plt.suptitle('Rewards taken vs opportunities missed')
    plt.show()

def exportGenometoCSV(filename, population):
    import csv
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)

        for member in population:
            writer.writerow(member[0] + member[1])
