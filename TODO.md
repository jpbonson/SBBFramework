===
TODO:

runs:
- initial results:
    results1
    - only_coded x2 (from test: [0.5139 to 0.534, very stable], train: [0.51602 to 0.56009, quite unstable], time: 43600 secs)
    - only_sbb x2 (from test: [0.50984 to 0.52742, mostly stable], train: [0.50032 to 0.49283, very unstable], time: 63406 secs)
        - is too slow (at least 50% more than only_coded, since it dont use memory) and produced below average results
    - hybrid x2 (from test: [0.5139 to 0.53163, very stable], train: [0.51901 to 0.52942, more quite unstable], time: 49318 secs)
        - very similar results for test, but for train the scoe is much lower than only_coded, just a bit slower
    - hybrid+hall of fame x2 (from test: [0.5139 to 0.53469, mostly stable], train: [0.53002 to 0.52838, very unstable], time: 42392 secs)
        - hall of fame seems to have improved the test results, but the train results are more unstable, similar runtime
    - only coded+equity+hall of fame x2 (from test: [0.50992 to 0.51701, very unstable], train: [0.52013 to 0.52337, very unstable], time: 37316 secs)
    - only coded+equity+hall of fame x1 (from test: [0.51677 to 0.53499, mostly stable], train: [0.54409 to 0.50364, very unstable], time: 37316 secs)
    - only_coded+equity+potential x1 (from test: [0.50656 to 0.53591, very stable], train: [0.50173 to 0.54714, very unstable], time: 48677 secs)
        - it took more generations to improve, but improved more than just only_coded
    others:
        - best option: only_coded + hall_of_fame? not sure if hall_of_fame is helping or not
        - usar equity_deck seems to provide faster results without decreasing the quality
        - hand_potential seems to decrease to quality, but should be tested more
        - com a melhor combinacao, testar apenas fold, call e raise, e testar random?
    results2
    - full_deck for hand_strength (ok) and equity 1/3 for hand potential (fazer testes rapidos?), balanced: True
    - balanced: False (check memory!)
        - training a bit more balanced
        - seems to be a bit more faster
        - sightly less stable test
        - inconclusive: would need to test for more runs

- pensar sobre:
    - salvar opponent model dentre dos objetos team?
    - fazer com que a segunda hand use a mesma seed, mas na outra position?
    - com apenas 2 hands, nao ha diferenca entre long e short agressiveness e volatility!
    - gerar uma seed diferente para cada hand do oponente?
    - agressiveness e volatility por tipo de oponente? opponent model modelar por tipos de oponentes (e ser aprte da classe Team? resetar quando mudar de generation?)?
    - se apenas 2 hands com mesma seed mas diferente positions, a segunda hand nao pode suar a info de agressiviness e volatility na primeira
    - e os chips? acumula entre hands?
    - "100 hands against each opponent/type of opponent"
    - 10 hands por 10 opponents eh mais rapido que 2 hands por 50 opponents? muda a performance? (considerar memory per point e tempo geral de processamento)
    - se usar swap, a point population poderia ser apenas as seeds das hands?

    So I was thinking a bit more about the point population... It seems to me that a point should contain a seeded opponent, a seeded hand, and a position, so that a point is able to differentiate a team from other teams, and between themselves, consistently. Another option would be a seeded opponent and a seeded hand, but played two times, one for each position.
    The problem is that, this way the inputs chips, agressiveness and volatility are mostly useless, since they are reseted when the team plays against new points.

    A further option, so that these three inputs can be useful, would be to store and update them during the generation, per opponent type. So if the point population is composed of 20 TypeA and 20 TypeB opponents, when a team went against the last TypeA opponent it would have a memory of how many chips it lost/won to the other 19 TypeA opponents, and a track of its agressiveness and volatility. Similar to a tournament, per opponent type. But I wonder if this sort of approach would be a problem since it would bias the teams actions for the last points of a same type of opponent (ie. the point order would be relevant to how well they differentiate teams, so it would impact the point selection). All teams play against the points in the same order, so there wouldn't be a problem regarding different teams seeing the 'tournament' differently.

    Right now the implementation has each point storing a seeded opponent, and two different seeded hands (one for each position), and has the problem with chips, agressiveness and volatility being useless. I would like to discuss more about the point population with you two before modifying the system 
    to one of the ideas I said above, so I will wait for feedback. While I wait I will keep implementing the things we discussed in the last meeting (the diversity and run outputs).

    (e resetar os inputs no comeco de uma nova generation)

implementar:
- alterar points para tambem terem position
- gerar metrics de validation para hall of fame antes de salvar

garantir outputs (for tictactoe and poker):
- analisar quais inputs estao sendo usados (apenas dos programs ativos no team): OK
- accumulative performance curve for the population (tutorial, page 27): TODO
- diversity x fitness x generations (for both diversities, violin plot? line plot?): TODO
- how the point population evolved over time (check the paper Malcolm talked about): TODO
- outputs para R plot: TODO

implementar:
- implementar mudancas na point population

ler papers:
- paper com os plots relevantes para a point population (esperar resposta do email?)

---

future work:
- implementar mais diversity: entropy
- fazer system tests para poker?
- implementar novos oponentes (opcao de agrupar oponentes por tipo?)
- permitir rodar point populations agrupando opponents for grupo, e sem agrupamento
- nos testes, checar se os teams sabem blefar
- refatorar codigo
- ir testando enquanto implementa:
    - (pc de casa, pc do lab (4 cores), NIMS server (6 cores), Hector, e Bluenose(?))
- steps:
    3. better opponents
    4. opponent model
    5. second layer
    6. more player? unlimited bets?

- extra:
    - fazer reinforcement learning para Othello?
    - implementar um tradutor que usa teams salvas em .json
        - deve ser possivel usa-lo para testar um time no ambiente
        - deve ser possivel usa-lo para treinar mais um conjunto de teams
            - se o pop_size nao for o suficiente, deve preencher o pop_gap com random ou children
    - implementar o second layer do SBB
        - no layer 2 do SBB os teams do layer 1 ficam frozen e sao usados pelo layer 2 como se fossem 'programs'
        - objetivo do layer 1: produzir uma population de team com alta diversidade
        - objetivo do layer 2: obter o melhor jogador de poker

- papers:
    - nos papers: se possivel, comprar SBB com outros poker players (alem de comparar o SBB entre si para diferentes configuracoes)
    - paper deadlines: january and march

- quando der tempo:
    - experimentar violin plot na R language (our usar http://matplotlib.org/examples/statistics/violinplot_demo.html e integrar no pSBB?)
    - usar import logging para nao floodar a tela com prints qd um test falhar
    - melhorar README.md
    - fazer mais testes unitarios (pareto, diversity, selection, matches, operations, program execution)
    - adicionar mais documentacao no codigo
    - remover comentarios em portugues

- performance:
    - futuro: usar cpython, cython ou similar?
    - usar mais map, reduce, e filter / list comprehension
    - armazenar function calls do lado de fora do loop quando possivel
    - range => xrange

========
Observacoes:
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

========
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

========
NOTES:

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