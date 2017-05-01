from deap import tools, base, creator, algorithms
import random

#evaluate score maximizing financial gains and minimizing missed oppotunities
def evaluate(member):
    score1 = 0
    score2 = 0
    offerAmts = (''.join(map(str, member[1])))
    return score1, score2


def makeDecision(offersLeft, member):
    decision = 0

    offer = (''.join(map(str, member[1])))
    offer = int(offer, 2)
    print "offer:\t" + str(offer)

    decision_bit = member[0][offer]
    print "decision bit:\t" + str(decision_bit)

    if offersLeft == 0 or decision_bit == 0:
        decision = 0
    elif offersLeft > 0 and decision_bit == 1:
        if offersLeft > 8:
            decision = 1
            offersLeft -= 1
    elif offersLeft > 0 and decision_bit == 2:
        if offersLeft > 4:
            decision = 1
            offersLeft -= 1
    elif offersLeft > 0 and decision_bit == 3:
        decision = 1
        offersLeft -= 1

    return [decision, offersLeft]


def mutateFlipBit(individual, indpb=0.1, indpb2 = 0.0):
    decisionSlice = individual[0][64:]
    genome = (individual[0][0:64])
    genome = (list)(tools.mutFlipBit(genome, indpb))

    fullGen =  genome[0] + (decisionSlice)
    individual[0] = fullGen
    #individual[0] = individual[0].pop(0)
    testvar = random.random
    if testvar < indpb2:
        individual[5] = random.randint(0,3)
    return individual, #comma here
