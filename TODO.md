Done (most recent):
added more debug messages + changed balance to 10/30/60
added more inputs to opponent model
changed volatility default to 0.5
removed sbb_extra_label and opp_extra_label
implemented stateful registers for reinforcement tasks
updated hands to balance pstr_ostr + fixed point cache
removed balanced_based_on and opp_label_
defined groups for diversity as 3
v2: gen100 and no self inputs + bug fix
v3: updated config + automated top5,top10,top15
v4: updated config + removed short-term opp model
reorganized point_generator and poker_analysis + not using ACPC for hand generation anymore
adapted code to used new poker hands
finished new code for poker match
fixed diversity entropy (c2 and c3)
minor improvements on diversities + updated README instructions
fixed bug in poker_match + added logs to poker_match + fixed bug in poker_opponents
selecting points using age instead of uniform probability
improve folder name
improved hand_played metric
added 'main metrics' to run_info
improved group metrics per run + added option to select poker opponents
added option to run river only
added program bid winner to poker log
added mean and std result as metric + fixed bug with validation and champion population sizes
fixed max ncd + rounding report metrics
remvoed pot and volatility
removed input 'bet' and rmeoved option LA_to_all
refactored OpponentModel + added inputs 'bluffing' and short-term self and opp aggr
fixed hall of fame in class reinforcement learning
saving more files for second layer + saving acc curves per run
fixed hall of fame
---

- mandar rodar second layer para 600 matches (com a melhor combinacao? parte no hector?)

- fazer charts para resultados do hall of fame (baseline, com 1 opp, com 2 opps, com 1-2 opps)
- fazer charts para resultados do river only (baseline, river_only, fullgame_only)
- implementar gerador de familia de points



report:
- experiments with river only to fullgame (vs only fullgame e only river)
    - also experiments with varying number of static opponents and quantity of generations and teams
    - updated inputs
- experiments with matches
- experiments with hall of fame
- experiments with second layer
- idea based on monte carlo (mantains the good performance and uses averaged results, problems: less variety of hands, may mess up with the long-term inputs)
- evolving opponents? is it worth it?
- focus on new ideas or focus on wrap up what I have and start writing the thesis?
- teach one class in GP about poker+SBB?

- 600+100hf+1-2opp (1), top5_overall_subcats (2), 
- hall of fame: 600 (1) matches, 600+100hf+1-2opp (2, backup)
- hall of fame: 600 (2 opps, 31370, e 1 opp 31396),  only_fullgame (5, 1326), only_river (6, 1330)

- esperar mais generations antes de ativar o hall of fame? (para ter opps mais interessantes e executar mais rapido)
- gradualmente aumentar de 0 hf, para 1, para 2?
- obs.: desse jeito, esta se comecando com menos points e aumentando aos poucos

- second layer
    - usar outra seed, fullgame_only
    - fazer poker_analysis funcionar para second layer (.json salvar as teams de cada action?), e para 'use_atomic_actions'
- performance profiling
    - passar operations para c?
    - melhorar codigo generate_profile em team.py? (ou chamadas a esse codigo em selection)
    - fazer profiling com um run de verdade? set de 2 runs?
- conferir como papers validaram os resultados (em especial, os em journals bons)
    - + fazer doc com exemplos de charts usados nos papers de SBB + outros papers
    - ver como hall of fame foi usado nos papers
- parameters to test:
    - what diversity? mix diversities? (entropy_c3, hamming_c3, ncd_c3, ou ncd_c4?)
    - profile size? team size? more...? (generations, matches...)
- adiantar mais o literature_review
    - comecar a escrever com os papers q já tenho (nao escrever coisas q podem mudar ainda)
    - selecionar references que parecem promissoras (apenas dos papers mais recentes ou mais classicas, ou do Billings)
    - define pages/paragraphs for each section
    - write (nao necessariamente rpeciso usar todos os papers para cada section)
- extras
    - fazer printar avg de behaviors do time no poker analysis
    - refatorar classe OpponentModel (separar self e opponent)
    - coevolving opponents? (evolving rule-based opponents e opponents q maximizam a diversity?)
- monte carlo?
    - no final, um team precisa participar de matches e receber uma fitness
    - monte carlo tree search nao parece fazer sentido nisso
    - alternativa:
        - ao inves de haver um point A (com 4 hole cards e 5 board cards), ha uma familia A (apenas as 4 holes cards? 2 hole cards? 4 hole cards e 3 board cards?)
        - precisa ser de um jeito q possa ser calculado os resultados fora do training?
        - como fica o balanceamento de hand strength nos points? (por familia de 4 hole cards?)
        - o mesmo team e oponente tem que ir contra todos as combinacoes de uma familia
        - risco de combinacoes nas familias nao fazerem diferenca, afinal as 4 hole cards iniciais nao mudam?
        - quando gerar as familias de combinacoes, obrigar que a board strength final para pelos menos um dos players seja diferente em pelo menos 2 pontos de alg combinacao q ja exista?
            - cuidado para nao travar! limitar numero de tries?
            - ou gerar combinacoes aleatorias e pegar o set de combinacoes com maior variancia de board strength?
        - 10 combinacoes por familia?
        - poe atrapalhar os inputs de short term, ja q vai ter um bias para a familia atual
        - how select the most disperse values/tuples in an array?
            - ir selecionando o mais disperso e removendo do array?
            - select min, max, e quartiles (25, 50, 75)?
            - [*, -, -, -, *, -, -, -, *, -, -, -, *, -, -, -, *]
            - len 9, 13, (x*4+1, para ser possivel pegar os percentiles 1, 25, 50, 75, 100)
            - combinar os valores da tupla? fazer percentiles separados por lista de tuples?
            - http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.percentile.html#numpy.percentile
            - ou:
            - euclidean distance? calculate it for all the other points and get a mean distance? (as in diversity!)
                - select the k ones with higher distance, and also the median? or the quartiles?
                - usar knn?
                - testar e analsiar o que sai
            

---

nims pc:
- ...

nims server:
- ...

hector server:
- ...


diversity:
- best_config_layer1_entropy_c2_seed5, 1, 
- best_config_layer1_entropy_c3_g3_seed5, 2, 
- best_config_layer1_euclidean_g3_seed5, 3, 
- best_config_layer1_fitness_sharing_seed5, 4, 
- best_config_layer1_genotype_seed5, 5, 
- best_config_layer1_hamming_c3_g3_seed5, 6, 
- best_config_layer1_ncd_c4_g5_seed5, 7 
- best_config_layer1_no_diversity_seed5, 8, 

---
scp -r source_file_name username@destination_host:destination_folder
scp -r username@destination_host:destination_folder source_file_name

=====================
- 6 hours per 5000 hands (total 10000 hands)

future work:
- more players in the table?
- nos testes, checar se os teams sabem blefar
- refatorar codigo
- ir testando enquanto implementa:
    - (pc de casa, pc do lab (4 cores), NIMS server (6 cores), Hector)
- permitir um player humano jogar contra um time SBB? (e outros players de AI tambem)
- tentar tournament + deterministic crowding? (papers [1][12])
- coded opponents com bluffing e showplaying?
- ler mais sobre como a solucao de poker da universidade de alberta funciona? qual oponente e' usado?
- tables com 4 ou 5 players?
- a funding de novembro, posso usar se eu trabalhar a distancia no brasil?

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

----------------------

##### Results using Mann-Whitney U-Test (http://www.socscistatistics.com/tests/mannwhitney/Default2.aspx):
### COMPARISON REGARDING PARETO FRONT
THYROID_DEFAULT < THYROID_WITH_PARETOS:
The U-value is 137. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is -3.3955. The p-value is 0.00068. The result is significant at p <= 0.05.
THYROID_WITH_PARETOS == THYROID_WITH_PARETO_FOR_TEAM_ONLY
The U-value is 278. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 0.6597. The p-value is 0.50926. The result is not significant at p <= 0.05.
THYROID_WITH_PARETOS > THYROID_WITH_PARETO_FOR_POINT_ONLY
The U-value is 190. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 2.3671. The p-value is 0.01778. The result is significant at p <= 0.05.
THYROID_WITH_PARETO_FOR_TEAM_ONLY == THYROID_WITH_PARETO_FOR_POINT_ONLY
The U-value is 219. The distribution is approximately normal. Therefore, the Z-value can be used.
The Z-Score is 1.8045. The p-value is 0.07186. The result is not significant at p <= 0.05.