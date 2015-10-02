Done (since summer report):
minor fixes (round_value para acc curve, salvars ids na acc curve, time in mins, distribution of inputs per teams)
minor fixes (fixed -1 in num_lines_per_file_, refatorar update_opponent_model_and_chips)
minor fixes (fixed bug with diversity across runs metric, fixed unit tests for ttt, checked alfa and beta for poker opponents + fixed bug + removed workaround)
minor fixes (refactored evaluate_point_population)
modifed EHS to EP + normalizing values between 0 and 10 + modified ppot
minor fixes (fixed 2 intron removal bugs)
minor fixes (min size for programs is 1)
using new EP input + normalized between 0 and 10 + opponents using HS + fixed bug for swap instruction when len = 1
minor fixes (fixed bug where ncd wasnt working for hall of fame + more 1000 hand samples)
minor fix (added index before input when printing)
more 5000 hand samples
minor fix (apply 'normalize_by' to classification and ttt)
minor fix (remove poker code from reinforcement learning environment (evaluate_team))
minor fix (storing in team metrics the last opponent they played against)
minor fix (refactored PokerConfig)
more 5000 hand samples
minor fix (store the fitness for the generations with the same diversity/opponents)
refactored calculate_accumulative_performances
minor fixes (fixed bug when no diversity is being used + accumulative curve per hands won and played (without subdivisions))
minor fixes (added subdivisions to accumulative curve per hands won and played)
minor fixes (added all subdivisions to all accumulative curve metrics)
minor fixes (moved files to folder 'core' and examples to 'tools')
minor fixes (refactored some of the poker code)
minor fix (fixed bug with formula for chips)
minor fix (implemented accumulative curve per opponent type + minor refactoring of poker code)
minor fix (refactored TODOs)
implemented option to use hall of fame without using it as opponents
minor fix (saving action_sequence as letters instead of numbers + fixed bug with hall of fame metrics)
modified NCD so now it uses state information (action + seed + position + board)
minor fixes (changed label for sbb_sd, now 2 == always worst, 0 == always best + fixed bug were opp_label wasnt using ostr + metric for training-only active programs)
-1. summer_report_fine_tuned
renamed some metrics, added new doc, added literature review latex, separated action sequence between ncd and entropy
fixed bug with the aggressiveness formula (affected last action in the sequence)
implemented hamming distance + ncd and entropy per hand
implemented NCDv2 and euclidean distance
-2. poker_report_diversities
added 10k more hand samples
refactored new diversities code + added unit tests
added metrics for mean team size and mean program size
removed print of metrics per run
added unit tests for all the new diversities
added option to choose uniform or weighted selection + unit test
changed opponent model (using all inputs)
added operations for signal-ifs
modified introns removal
removed references to PokerMetric to avoid useless import
fixed import for introns removal test
fixed dumb bug
moved files run_info and operations
merged main and main_for_poker
implemented pruning
implemented bid profile + updated is_nearly_equal_threshold + replace = True for cloning
fixed run_initialization_step2 + added unit test + fixed unit tests
added option to use agressive mutations team add/remove mutations + added unit tests
removed sigmoid function
-
implemented json reader json for teams
added metric for final team validations
---

results:
- profile2 (?)
- use_weighted_probability_selection_True
- run_initialization_step2_False


- implementar tasks do second layer
- fazer run no diversity
- Fazer doc com exemplos de charts usados nos papers de SBB + outros oapers




---
parameters to test:
- what diversity? how many groups? mix diversities? (temp: ncd_c3, g5)
- what balance? (temp: board)
- +inputs? (temp: all, check it better in the next runs)
- ifs? (only normal ifs, only signal-ifs, or mixed? temp: mixed)
- groups 3 or 5? (temp: 5)
- team size and program size? (testar apos obter reusltados para diversities?)

nims pc:
- default_no_sigmoid_profile5, seed 1, 1
- default_no_sigmoid_profile5, seed 2, 2
- default_with_new_outputs, seed 1, 3

nims server:
- SBB3, use_agressive_mutations True, seed 2, 7, 11181
- SBB4, default_with_new_outputs, seed 2, 8, 11333
- SBB5, default_with_new_outputs_with_hall_of_fame, seed 1, 9, 8837
- SBB5, default_with_new_outputs_with_hall_of_fame, seed 2, 10, 17846
- SBB1, default_newest_best_seed1, 1, 7627
- SBB1, default_newest_best_seed2, 2, 13261

hector server:
- run_initialization_step2 True, seed 1, 1, 4314
- use_weighted_probability_selection True, seed 1, 2, 8142
- use_agressive_mutations True, seed 1, 3, 12209
- default_no_sigmoid, seed 2, 4, 4739
- default_newest_best_no_diversity_seed1, 5, 
- default_newest_best_no_diversity_seed2, 6, 


---
- second layer:
    - second layer SBB: It is exact the same thing, the only modification is when an action is called
    - for the second layer, two approaches:
        - get the teams that most increased the accumulative curve across all the runs
        - get the teams that most increased the accumulative curve individually for each run
        - obs.: be careful when selecting the teams what will be action, so the search space is not so big
    - steps:
        - generalize the call of actions, the definition of actions, and the mapping of actions
            - add a new class that hands the action calling/definition/mapping
            - metodo get_action_result?
            - fazer classe Action?
            - no lugares onde action eh repassado (team mutation), conferir se precisar usar deepcopy ou apenas por referencia esta ok
        - select the best saved teams
        - check if it works as it is
        - quando escolher time spara o second layer, conferir se todos os inputs estao sendo usados! e que os teams variam as behaviors!
        - add unit tests for ttt

---
- adiantar mais o literature_review
    - select papers for each section of the literature review
        - for all TODO papers, relate them with the sections
        - find papers for the sections with no papers (conferir tanto nos papers ja usados como os nao usados)
    - dividir capitulos SBB e SBB+poker em sessoes
    - selecionar references que parecem promissoras (apenas dos papers mais recentes ou mais classicas, ou do Billings)
    - define pages/paragraphs for each section
    - write (nao necessariamente rpeciso usar todos os papers para cada section)

---
- coevolved opponents population:
    - Competitive coevolution, host-parasite
    - freeze SBB while evolve opponents, then freeze opponent, then SBB, etc...?
    - use what version of SBB? layer 1? layer 2? layer 3? (preference for keep evolving layer 2)
    - opponents evolving as alfa/beta from the paper poker_evolutionary_bayesian_opponent_model 2007 and 2008
        - or the poker_evolutionary 1998 and 1999?
        - preference for the earlier one
    - check the notes about the new coevolved opponent population (alfa/beta)
    - try to use pareto to select the teams that perform better against various opponents?
    - or just one opponent per generation?
    - usar algoritmo da pagina 99 para gerar oponentes? (ver em sbb_papers) como selecionar fitness dos oponentes? pareto de distinctions? ou uniform probability? tomar cuidado com class balance?
        - removal: usar pareto com distinctions
        - selection para clonar: usar uniform probability
    - thesis do peter: Pages 103-108: outra maneira de remover points baseado em distinctions, sem ser pareto
        - tamblem no paper "complexification", em "points removal" (ver em sbb_papers)

---
(optional?) final opponents
- ver o q papers de poker recente usaram para validar/como oponente final
- implement static opponents so the best team can go against and check if they have strong poker strategies
    - [5](o sistema desenvolvido)
    - [6](os benchmarks)

---
- usar pop 80 ao inves de 100?
- before running the 10 runs of all the diversties, define a good generation to stop and the parameters
- no inicio, rodar para apenas G3 ou G5, nao para os dois (provavelmente apenas um iria para um paper anyway)
- perform various runs on hector for the different diversities, at least 10 of each (an plot them with a box plot)
    - dont use bluenose!
    - use the command 'nice'

---
scp -r source_file_name username@destination_host:destination_folder
scp -r username@destination_host:destination_folder source_file_name

=====================
future work:
- nos testes, checar se os teams sabem blefar
- refatorar codigo
- ir testando enquanto implementa:
    - (pc de casa, pc do lab (4 cores), NIMS server (6 cores), Hector)
- permitir um player humano jogar contra um time SBB? (e outros players de AI tambem)
- tentar tournament + deterministic crowding? (papers [1][12])
- coded opponents com bluffing e showplaying?

- steps:
    3. better opponents
    4. opponent model
    5. second layer
    6. more player? unlimited bets?

- futuro:
    - layer 1:
        - objetivo:
            - boa diversity: accumulative curves bem separadas
            - teams devem aprender como usar as hand types
            - o foco nao e' oponentes, entao usar oponentes dummy com pouca variacao
    - layer 2:
        - objetivo:
            - teams devem aprender como lidar com diferentes opponents, mais dificeis
            - adicionar uma population de opponents que evolui com coevolution, usando pareto

- extra:
    - implementar um tradutor que usa teams salvas em .json
        - deve ser possivel usa-lo para testar um time no ambiente
        - deve ser possivel usa-lo para treinar mais um conjunto de teams
            - se o pop_size nao for o suficiente, deve preencher o pop_gap com random ou children
    - implementar o second layer do SBB
        - no layer 2 do SBB os teams do layer 1 ficam frozen e sao usados pelo layer 2 como se fossem 'programs'
        - objetivo do layer 1: produzir uma population de team com alta diversidade
        - objetivo do layer 2: obter o melhor jogador de poker
    - conferir paper Learning Strategies for Opponent Modeling in Poker, para mais inputs (e resultados) e "An Investigation into Tournament Poker Strategy using Evolutionary Algorithms, 2007" para uma analise de quais inputs se saem melhor

- papers:
    - nos papers: se possivel, comprar SBB com outros poker players (alem de comparar o SBB entre si para diferentes configuracoes)
    - paper deadlines: january and march
    - implementar scripts em tools para printar os charts (violin, line, etc), python or R? conferir papers do SBB, GP e tutorials para ver os charts mais usados
    - perguntar se o paper Ideal Evaluation from Coevolution foi usado como base para a point population evolution com pareto na versao original do SBB

=================================================
Quando der tempo:
    - fazer versao do pSBB sem poker, para ser open source, e mover poker para um branch
    - experimentar violin plot na R language (our usar http://matplotlib.org/examples/statistics/violinplot_demo.html e integrar no pSBB?)
    - usar import logging para nao floodar a tela com prints qd um test falhar
    - melhorar README.md
    - fazer mais testes unitarios (pareto, diversity, selection, matches, operations, program execution)
    - adicionar mais documentacao no codigo
    - remover comentarios em portugues
    - fazer reinforcement learning para outros jogos? (Othello?)
    - performance:
        - usar cpython, cython ou similar?
        - usar mais map, reduce, e filter / list comprehension
        - armazenar function calls do lado de fora do loop quando possivel
        - range => xrange

=================================================
Observacoes:
- o correto e' calcular as validation metrics apenas para os parents mesmo
- cada dimensao da point population eh uma das dimensoes q vai ser maximizada no pareto, gerando as poker behaviors
- tomar cuidado com: cycling. disingagement, overspecialization, forgetting
- Reward for point population:
    - Distinctions: reward tests for every pair of solutions they distinguish
    - Informativeness: reward tests for unique partitioning of S

Guidelines:
- usar apenas um _ no methods
- usar _ no final dos internal classes attributes (que nao vieram de parametros)

jSBB:
- teams always start with 2 learners
- programsize = fixo
- mutation de programas: add, remove, swap e change_instruction
- tratamento para overflow (usar valor anterior vs zerar)
- if (ser um if mesmo vs mudar o sinal do regsitrador)
- se children tiverem os mesmos learners que os parents, obriga a mutacionar
- novos learners naquele time só são gerados mutacionando outros learners daquele mesmo time (ao inves de globalmente)
- tem mutation de swap instructions

=================================================
Parametros no paper:

generations: 1000
point population: 120
team population: 120
point replacement rate: 0.17
team replacement rate: 0.5
team max size: 10
pmdelete: 0.7
pmadd: 0.7
pmm: 0.2 (chance de programa ser mutacionado)
pmn: 0.1 (chance de programa mudar action)

num_registers: 8
pdelete, padd = 0.5
pmutate, pswap = 1.0
max program size = 48

=================================================

Notes 29/09/2015

Then, I read the SBB description in Peter's thesis and in the paper "Symbiosis, Complexification and Simplicity under GP" again, to ensure that there wasn't anymore minor details missing. The things that pSBB and Peter's SBB differ are below. I will show up at the lab this week to get your signature in the add/drop form, so we may talk about these points in the lab instead of by email (I am available any day by the afternoon).

-------------

- prunings of inactive programs  (3.3.1. in Peter's thesis): I added this feature to the default run of pSBB (it didn't change the results much, but now the final teams are around half the size).

- use bid profile to ensure that children have a bid profile different from all the teams currently in the population  (3.3.2. in Peter's thesis): Added to the default run of pSBB (I am performing runs to find the best value for the profile size (between profile pop. size == point pop. size, ==point pop. size*2, and point pop. size/2), and I still don't have results if it indeed improved the diversity).

- second step of initialization (3.3.3. in Peter's thesis): I added it as an optional parameter. My initial results suggest that it increased the runtime without really improving the results, it also seems against the idea that the hosts should start simple and then complexify. So I will test it a bit more, but I probably will not use it.

- mutations (algorithms 3.3 and 3.4 in Peter's thesis): In pSBB the add/remove mutations may occur just once, with a probability of 0.7. In Peter's version there is always at least one add/remove mutation, and more than one may happen with a decreasing probability of 0.7. I added Peter's mutations as an optional feature called 'agressive mutations'. I am still testing these options, but the 'agressive mutations' seems to be too disruptive and I will probably end up with my version of mutations.

- point removal (3.2.6. in Peter's): Currently the point removal is performed using only uniform probability. I had performed some tests using pareto to identify distinctions but they didn't produce good results. I thought that Peter had used pareto, but he actually used a different algorithm and argued against pareto. I think this algorithm still isn't useful for the first layer anyway, since it would reinforce points that are being mostly folded, but I will try to use it to control the point population based on opponents for the second layer.

- sigmoid function: I am using the sigmoid function as described in the paper's but I was analyzing it and it seems to have a problem: Any value bigger than 37 is rounded to 1.0, and any value lower than -746 is rounded to 0.0 (due to float point precision). Since the inputs are normalized between 0 and 10, and some of the available operations are +,*, and exp, and I am pretty sure that outputs greater than 37 are very common, and when it happens with more than one bid, the winning bid is arbitrary. Peter states that '[sigmoid] is used to encourage individuals to compete over a common range of bids', but I think that all values greater than 37 being converted to 1.0 is probably losing useful information. To work around this problem, I will test always divide the ouput of the program by 10000000 before applying the sigmoid, to artificially increase the input range from [-746, 37] to [-7460000000, 370000000](the only thing that I lose doing it is that float outputs will be truncated after the 8th position, instead of after the 15h position).

- parameters: the previous works with SBB had a point/host population slightly bigger, and considerable bigger team size, program size, and more registers. Since as it is right now pSBB for poker already is slow enough, I will keep my current parameters as they are, but I intend to try with larger parameters after I get overall results for the current ones.

=================================================
NOTES:

1 hand for 2 always raise opponents:
scores: ['240', '-240']
players: ['sbb', 'opponent']
normalized_value: 1.0

showdown:
- I was thinking if in some way the result of the showdown could be useful for the SBB player (during and after training), e.g. be able to know if the opponent was bluffing or not. An option would be to create an input "% of showdown hands the opponent has bluffed", but then it woulb be necessary to implement a way to define what is or isn't a bluff.

opponents:
- instead of balancing opponents in each generation, just use different point populations for each opponent and uniform randomly swap them across generations (in order to have a better control over the gradient of learning, and this was the result of a paper that Malcolm pointed out). If possible, mantain the option to balance opponents so these options can be compared.
        - example of type of opponents:
            - tictactoe: random, smart, self-play, hall of fame
            - poker: always fold, always raise, always call, agressive, defensive, smart

- inicializar apenas meia populacao? (para ficar mais facil reutilizar depois?)
    - nao, inicializar com toda a populacao sendo random da mais diversidade e um search space mais amplo
    - o que pode ser feito no futuro, quando for reutilizar populacoes (ou seja, usando pop_size - pop_gap) posso dar as opcoes de:
        - preencher o gap com novos teams randomicos
        - preencher o gap com children dos teams em pop_size

- initialize teams with 2 different actions (instead of 1 action per available action. In order to start simple and complexify over time, allowing SBB time to understand and mix the simpler teams and programs. It is necessary to use a higher number of generations.)
- the initial teams must have unique sets of programs (in order to start with the maximum diversity)

solutions can be optimally: local (self-play), global (opponents), historical (hall of fame), end goal: global

pareto:
    - helps keeping populations coupled?

poker table:
    - each point is a table, and contains a set of opponents (that dont need to be balanced, ie. a table full of opponents that always fold is ok)

anotacoes sobre hall of fame:
    - different from the one in Countering Evolutionary Forgetting in No-Limit Texas Hold’em Poker Agents
        - the hall of fame was better than coevolution
        - but the intention here is for it to be complementar
    - usar o champion a cada validation?  usar best teams of each generation, usar fitness (em relacao aos teams daquela generation) ou diversity (em relacao aos teams no hall of fame, apenas a genotype diversity)? (se usar champion, fica mais complicado escolher quais teams manter no hall of fame)
    - hall of fame independente da point population
    - priorizar manter older teams? manter os com melhor fitness?
    - usar hall of fame na validation (apenas como metric, ou como criterio? por enquanto, usar apenas como metric)
    - comecar testando usar fitness, depois testar usando diversity?
    - tamanho do hall of fame configuravel? hall of fame deve ter o mesmo peso ou mais peso que um tipo de oponente regular? (por enquanto, vai ser um valor fixo configuravel, e entao pode ter mais peso que tipos de oponentes especificos)
    - utilidade: impedir comportamento circular (nao necessariamente obter melhores teams globalmente)
    - por enquanto:
        - hall of fame usado como criterio apenas no training, mas usado como metric na validation
        - o hall of fame tem um tamanho fixo configuravel definido em CONFIG
        - o melhor time de cada generation eh colocado no hall of fame
        - se o hall of fame lotar, descartar o time com pior fitness

anotacoes sobre self-play ['only_sbb', 'only_coded_opponents', 'hybrid']
    - encapsular teams em points (mas nao avaliar esses points em evaluate, novos points devem ser obtidos a cada generation da population atual)
    - alterar metodos que modificam point_population_ de acordo
    - selecionar teams com uniform probability? com weighted? (usando: weighted)
    - validation and champion population never use sbb_opponents (so they are always the same across runs)

    - improves self-play so the opponent sbb also improves its metrics? (just set is_training to True?) (is it worth to fix it? for the sbb opponent, it will seem as if the point population is much larger)
        - daria para habilitar que ambos os teams no modo self_play only atualizassem suas metrics com as matches se nem pareto e nem fitness sharing forem utilizados

Notes from meeting with Malcolm:

- sempre usar todos os opponents no training e na validation, nao apenas os fortes (senao pode ocorrer do SBB aprender a vencer 
apenas de oponentes fortes, e perder quando enfrentar os fracos)
- na validation usar apenas os oponentes fixos (nao os de self-play ou hall of fame)

- Final output of SBB runs:
    - best solution for every run (find them using the whole validation set in the last generation)
    - distribution of the results for the best solutions of each run (for scores, also for diversities?), using violin chart (R language)

- Como obter various poker playing behaviors? (all options using the validation set)
    - get the best ones per run, focusing in which opponents they are able to beat
    - apply pareto to try to obtain a diverse front
    - use a second layer (hierarquical SBB) to let SBB itself decide it