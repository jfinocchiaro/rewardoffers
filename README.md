# reward offers or Iterated Passenger's Dilemma

  Dependencies of this program include DEAP and some of the pre-installed python packages

  globals.py defines values needed in multiple files in the project

  realplayers.py contains a sample population of "actual people" that might accept on different conditions.

  binary.py has members with genomes consisting of bits, so mutation is generated as a bit flip

  conditional.py has a genome made of numbers 0-3, and rewards are accepted on a conditional basis (depending on a pseudorandom number generated if the person is "available" to wait an extra day to fly home.)

  pop_train_real_test.py trains a binary member against other members of the population

  real_train_real_test.py trains a binary member against out sample population and tests the best member from training against the sample population contained in realplayers.py

  customfunctions.py contains all of the hand-written (non-DEAP) functions used to evaluate players and will contain a hand-written mutation function for conditional.py, as well as functions to plot the members' fitness.
