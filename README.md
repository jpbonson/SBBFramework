# GeneticProgramming

Para usar no Windows, com o Anaconda:
python "C:\Users\jpbonson\Dropbox\Dalhousie Winter 2015\Genetic Algorithms\GeneticProgrammingSandbox\main.py"
E para acessar o Git:
cd "C:\Users\jpbonson\Dropbox\Dalhousie Winter 2015\Genetic Algorithms\GeneticProgrammingSandbox"

Quando mudar de SO, mudar a variavel CURRENT_DIR

Bug?

>>>>> Executing generation: 1, run: 1
Best program: 2:1, fitness: 0.935, accuracy-trainingset: 0.935, accuracy-testset: 0.92707, len: 32
Sampling

>>>>> Executing generation: 2, run: 1
Best program: 2:1, fitness: 0.935, accuracy-trainingset: 0.935, accuracy-testset: 0.92707, len: 32
Sampling

>>>>> Executing generation: 3, run: 1
Best program: 2:1, fitness: 0.935, accuracy-trainingset: 0.935, accuracy-testset: 0.92707, len: 32
Sampling

>>>>> Executing generation: 4, run: 1
Best program: 262:4, fitness: 0.955, accuracy-trainingset: 0.955, accuracy-testset: 0.92707, len: 44
Sampling

>>>>> Executing generation: 5, run: 1
Best program: 262:4, fitness: 0.955, accuracy-trainingset: 0.955, accuracy-testset: 0.02567, len: 44
Sampling

>>>>> Executing generation: 6, run: 1
Best program: 262:4, fitness: 0.955, accuracy-trainingset: 0.955, accuracy-testset: 0.02567, len: 44
Sampling

=============================================

Thus, for a classification task consisting of 3 classes, then
the legal set of actions from which an action can be selected are a action PERTENCE {1, 2, 3}. Each
individual within the BidGP population can only have a single action associated with
it.


The minimal criteria for a legal team are:
(a) there must be at least two BidGP individuals;
(b) the same BidGP individual can only appear within the same team once, but may
appear in more than one team;
(c) across the set of BidGP individuals associated with the same team, there must
be at least two different actions present.


With this in mind, we define an independent GA population to specify which BidGP
individuals appear in each ’team’ (Figure 1). That is to say, each individual from such a
team population specifies a unique combination of BidGP individuals forming a team.
Fitness will only be evaluated at the level of the team. Each individual in the team
population is merely a set of indexes to individuals in the BidGP population.

for each sample k
- evaluate each GP of the team
- get the action of the GP that got the highest output
- the GP's action is the prediction that will be used to evaluate fitness

associar actions randomicamente qd um GP e' criado



In the case of a generational model for the selection operator, the following process is
recommended:
1. Identify the worst Gap% team individuals and delete them;
2. Test for any BidGP individuals that are not used by the remaining (100 -��� Gap)%
teams and delete them;
3. Create Gap% new team individuals using the variation operators (example definition
below).


Initialization of team and BidGP populations assumes the following form:
1. Initialize a BidGP population of size 2 x H in which each action are equally probable
(program initialization follows the same heuristic as you have previously assumed).
2. Initialize a team population of size H with each team consisting of 2 to w team
members (such that the above conditions on actions per team are satisfied).


Mutation, after selection, to replace the removed %Gap tema:
1. Choosing a team currently in the team population to clone (say with uniform p.d.f.);
2. Identify one or more BidGP individuals to remove and / or add (from the team)
while enforcing the criteria for a legal team (see first bullet point);
---
If BidGP population size < 2 x H, then you can also consider the case of adding new
individuals to the BidGP population. Such a process would begin by cloning a BidGP
individual that one of the new Gap% teams indexes. Only after cloning a BidGP individual
and updating the team pointer to index the cloned BidGP individual would you then
apply your mutation operators.


alterar programa para printar nova saida completa

removido crossover

para o programa ainda variar de tamanho, adicionada chance de uma isntrução ser adicionada (random) ou removida em uma mutação