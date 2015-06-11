===
TODO:

- meeting notes:

    - modify the teams in the initialization (randomly define the size of team, and then add already created programs to them)

    - permitir remover e adicionar ate dois programs por vez p^(i-1), i range: [1, quantity of programs in the team]
        - a adicao eh feita em relacao a programs_population
    - na criacao de programs, ao inves de preencher a populacao: adicionar chance de um program ser mutacionado (pmm) quando o time eh clonado
        - esse operador precisa ficar sendo aplicado em todos os programs ate que pelo menos um program seja modificado
    - dont enforce a fixed number of programs per generation, this number should change depending on the mutation operators (modify Selection)
    - se apos adicionar programs o team ficar cheio, testar se algum dos programs nunca foi um active_program e remove-lo (nesse teste, ignorar os programas recem adicionados)

    - ?: se no final da generation houver programs que nunca foram ativos em nenhum team, remove-los (ignroar os que foram recem criados)

    - instead of balancing opponents in each generation, just use different point populations for each opponent and uniform randomly swap them across generations (in order to have a better control over the gradient of learning, and this was the result of a paper that Malcolm pointed out). If possible, mantain the option to balance opponents so these options can be compared.
        - example of type of opponents:
            - tictactoe: random, smart, self-play, hall of fame
            - poker: always fold, always raise, always call, agressive, defensive, smart

    - save more things when writing the outputs (both the metrics and the programs (and the .sbb file, if it is implemented already)):
        - the pareto front of the last generation
        - the hall of fame of the last generation
        - all the teams of the last generation

    - the size of the hall of fame is the size of the point population, and it should be swaped as the other point populations (to replace: use fitness? diversity? pareto?)

    - update system tests (classification and tictactoe)

- before the release/implementing poker:
    - adicionar _ nos atributos internos das classes e atributos novos
    - ler paper do SBB e conferir se tem algo errado ou faltando (Symbiosis, Complexification and Simplicity under GP)
    - fazer release no github

- ir testando enquanto implementa:
    - fazer example para tictactoe (fazer sets de 10 runs separadas?)
    - fazer example para thyroid (mas nao focar muito nisso)

- extra:
    - testar se o random do python gera os mesmos numeros aqui e no lab. Se nao gerar, tentar usar o random do numpy
        - values for Windows and Ubuntu at home:
        - random.seed(1), random.choice([0,1,2,3]): 0 3 3 1 1 1 2
        - np.random.seed(1), np.random.choice([0,1,2,3]): 1 3 0 0 3 1 3
        - np.random.RandomState(seed=1), a.choice([0,1,2,3]): 1 3 0 0 3 1 3
        - this warning occurs when running nosetests in lab:
            /usr/local/lib/python2.7/dist-packages/numpy/core/fromnumeric.py:2507: VisibleDeprecationWarning: `rank` is deprecated; use the `ndim` attribute or function instead. To find the rank of a matrix see `numpy.linalg.matrix_rank`.
        no lab, seed = 1:
            import random
            import numpy as np
            random.seed(1)
            np.random.seed(1)
            - random.randint(0, 4294967295): 577090034, 3639700185 (L), 3280387010 (L)
            - random.random(): 0.13436424411240122, 0.8474337369372327, 0.763774618976614
            - random.sample([0,1,2,3,4,5,6,7], 3): [1, 5, 4], [2, 3, 7], [5, 7, 0]
            - a = [0,1,2,3], random.shuffle(a): [3, 1, 2, 0], [2, 3, 0, 1], [3, 2, 1, 0]
            - np.random.choice([0,1,2,3], size = 2, replace = True, p = [0.3, 0.2, 0.2, 0.3]): [1, 3], [0, 1], [0, 0]

            em casa: 
            random.seed(1)
            - random.randint(0, 2147483647): 288545017, 1819850092, 1640193505
    - ver como fazer para executar runs de tictactoe no server do NIMS? (ver se tem como executar de casa atraves da maquina no lab)
    - usar threads ou processes para executar runs em paralelo?
    - add a way to reuse teams:
        - poder salvar os melhores times no formato objeto? ou como um array de sets de instructions? (para ser mais reutilizavel?)
        - implementar tradutor que le o objeto do time e computa resultados?

- starting poker implementation:
    - conferir se pareto e fitness sharing ainda funcionam mesmo quando a fitness sao vitorias ou dinheiro ganho (normalizar resultados? dividir pelo resultado maximo obtido?)
    - implementar poker environment (resetar os registers apos cada acao (ou logo antes) e point population: opponents (static, dynamic, itself), hands, positions), um point inclui a position, ou todos os points sempre incluem varias matches em todas as positions?
    - refatorar environments (criar environment de reinforcement?)

- quando der tempo:
    - experimentar violin plot na R language (our usar http://matplotlib.org/examples/statistics/violinplot_demo.html e integrar no pSBB?)
    - usar import logging para nao floodar a tela com prints qd um test falhar
    - melhorar README.md (sudo apt-get install build-essential python-dev ? usar virtualenv?)
    - conferir se requirement.txt funciona
    - velocidade de rodar? (pypy, cpython, or c)
    - fazer mais testes unitarios (pareto, diversity, selection, matches, operations, program execution)
    - adicionar mais documentacao
    - remover comentarios em portugues

===
Observacoes:
- cada dimensao da point population eh uma das dimensoes q vai ser maximizada no pareto, gerando as poker behaviors
- tomar cuidado com: cycling. disingagement, overspecialization, forgetting
- Reward for point population:
    - Distinctions: reward tests for every pair of solutions they distinguish
    - Informativeness: reward tests for unique partitioning of S

Guidelines:
- usar apenas um _ no methods
- usar _ no final dos atributos internos (que nao vieram de parametros)

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