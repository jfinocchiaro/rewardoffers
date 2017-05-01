from deap import tools, base, creator, algorithms
import random

#evaluate score maximizing financial gains and minimizing missed oppotunities
def evaluate(member):
    rewards = 0
    rewards = member[2][0]
    missedOpps = member[2][1]
    return rewards, missedOpps


def makeDecision(offersLeft, member):
    decision = 0

    #offer stored in genome as a binary number
    offer = (''.join(map(str, member[1])))
    offer = int(offer, 2)
    #print "offer:\t" + str(offer)

    decision_bit = member[0][offer]
    #print "decision bit:\t" + str(decision_bit)

    if offersLeft > 0 and decision_bit == 0:
        decision = 0
    elif offersLeft > 0 and decision_bit == 1:
        if offersLeft < 2:
            decision = 1
            offersLeft -= 1
            member[2][0] += offer
    elif offersLeft > 0 and decision_bit == 2:
        if offersLeft < 4:
            decision = 1
            offersLeft -= 1
            member[2][0] += offer
    elif offersLeft > 0 and decision_bit == 3:
        decision = 1
        offersLeft -= 1
        member[2][0] += offer
    elif offersLeft == 0 and decision_bit != 0:
        member[2][1] += 1 #missed opportunity increment
        decision = 0


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
