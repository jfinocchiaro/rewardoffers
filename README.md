# reward offers


TODO:
   X - remove reward offers from genome, add as parameter to makeDecision
   X - change genome to bits (or change conditions on accepting an offer)
   X - change mutation to bit flip
   make sure customer can only trade in per flight

LATER:
    custom mutation function (add 1, 2, or 3 mod 4)
    generate urgency of trip / genome back to 1-4


generation:
  x flights (try different numbers)
    progression of rewards until all accepted or rewards maxed

  binary.py has members with genomes consisting of bits, so mutation is generated as a bit flip

  conditional.py has a genome made of numbers 0-3, and rewards are accepted on a conditional basis (depending on a pseudorandom number generated if the person is "available" to wait an extra day to fly home.)

  customfunctions.py contains all of the hand-written (non-DEAP) functions used to evaluate players and will contain a hand-written mutation function for conditional.py, as well as functions to plot the members' fitness.
