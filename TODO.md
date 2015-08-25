Done:
minor fixes (round_value para acc curve, salvars ids na acc curve, time in mins, distribution of inputs per teams)
minor fixes (fixed -1 in num_lines_per_file_, refatorar update_opponent_model_and_chips)
minor fixes (fixed bug with diversity across runs metric, fixed unit tests for ttt, checked alfa and beta for poker opponents + fixed bug + removed workaround)
minor fixes (refactored evaluate_point_population)
modifed EHS to EP + normalizing values between 0 and 10 + modified ppot
minor fixes (fixed 2 intron removal bugs)
minor fixes (min size for programs is 1)
using new EP input + normalized between 0 and 10 + opponents using HS + fixed bug for swap instruction when len = 1
- 50 run
minor fixes (fixed bug where ncd wasnt working for hall of fame + more 1000 hand samples)
minor fix (added index before input when printing)
more 5000 hand samples
---
- fazer mais 10k samples (cuidado com 'w'!)

implementar + testar:
- implementar NCD using state information (hand type+position) + testar
- 10 ou 20 instructions? ou 15?

- apply 'normalize_by' to classification and ttt
- store the fitness for the generations with the same diversity/opponents
- conferir TODOs
- remover codigo de poker do reinforcement learning environment
- obter chips to resultado final da match quando for mudar de hand, ao inves de usar o valor temporario?
- accumulative curve per hands won?
- accumulative curve para mais coisas alem de sbb_label?
- atualizar opponent model para usar action_sequence do opponent?
- std dev dos scores per point type e per opponent type?
- salvar nas metrics do team qual foi o ultimo opponent type q ele enfrentou? (se hall of fame, printar tb o id do oponente)
- ajeitar arquivos em pastas core e utils

extra:
- conferir 'least regreat', usado pela University of Alberta?
- repassar comentairos do paper sobre NCD para o doc

=====================
Main Goals (next weeks):
- Find out if the current diversity metrics are being able to maintain diversity, based on the  accumulative performance curves.
- Find configurations that produce the best results (based on diversity and test score)
- (depois, se necessario) pensar em outra behavioral diversity metric (uma evolucao da entropy?)

future work:
- nos testes, checar se os teams sabem blefar
- refatorar codigo
- ir testando enquanto implementa:
    - (pc de casa, pc do lab (4 cores), NIMS server (6 cores), Hector, e Bluenose(?))

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