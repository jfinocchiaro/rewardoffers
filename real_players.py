import random
import math

from globals import rewards

# real member types:
#
# business:             never accept
# dude:                 accept any offer with high probability
# last:                 accept last available with probability 0.5
# ka-ching:             accept if round >= 4
# ka-ching+:            accept if last round
# linear-low:           accept at random -- prob increases with amount - max prob = 0.5
# linear:               accept at random - prob increases with amount - max prob = 1
# exponential:          probability of acceptance doubles each round


def getRealMix(length):
    l = []
    # about 12% of passengers, on average, are business travelers
    business_num = int(random.gauss(0.15, 0.06) * length)
    l.extend(['business' for i in range(business_num)])

    # there are likely to be a few passengers who will accept any offer
    dude_num = int(math.floor(length * .01))
    l.extend(['dude' for i in range(dude_num)])

    # num_left = length - len(l)
    # kaching_num = int(random.gauss(0.20, 0.06) * length)
    # l.extend(['ka-ching' for i in range(kaching_num)])

    last_num = int(random.gauss(0.08, 0.05) * length)
    l.extend(['last' for i in range(last_num)])

    exp_num = int(random.gauss(0.24, 0.06) * length)
    l.extend(['exponential' for i in range(exp_num)])

    exp_num = int(random.gauss(0.23, 0.06) * length)
    l.extend(['expovariate' for i in range(exp_num)])

    lin_low_num = int(random.gauss(0.20, 0.06) * length)
    l.extend(['linear-low' for i in range(lin_low_num)])

    l.extend(['linear' for i in range(length - len(l))])

    # len(l) may be > length
    # shuffle l so that elements at end of list have a chance of
    # getting into population
    random.shuffle(l)

    return l


def playVariedPop(oppName, round, offers, flight):

    # default decision is 0
    decision2 = 0

    # always decline
    if oppName == 'business':
        pass

    elif oppName == 'exponential':
        if random.random() < 1./2**(len(rewards) - round):
            decision2 = 1

    elif oppName == 'expovariate':
        if random.expovariate(len(rewards) - round) > 0.5:
            decision2 = 1

    elif oppName == 'linear-low':
        if random.randint(0, 40000) < rewards[round]:
            decision2 = 1

    elif oppName == 'linear':
        if random.randint(0, 20000) < rewards[round]:
            decision2 = 1

    # accept if one left
    elif oppName == 'last':
        if offers == 1:
            if random.random() < 0.5:
                decision2 = 1

    # always accept
    elif oppName == 'dude':
        if random.random() < 0.75:
            decision2 = 1

    # accept if two or fewer left
    elif oppName == 'last2':
        if 0 < offers <= 2:
            decision2 = 1

    # accept if round at least 4
    elif oppName == 'ka-ching':
        if round >= 4:
            decision2 = 1

    # accept if last round
    elif oppName == 'ka-ching+':
        if round == len(rewards)-1:
            decision2 = 1

    # random
    elif oppName == 'random':
        decision2 = random.randint(0, 1)

    # accept 2 offers if available
    elif oppName == 'couple':
        if offers >= 2:
            decision2 = 1

    # else
    else:
        print "Error invalid varied player"
        decision2 = -1

    return decision2
