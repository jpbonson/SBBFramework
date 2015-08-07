===
todo:
- 4 opponents based on equity (probabilistic?)
    If we build a couple of opponents that are more likely to engage in hands proportionate to starting equity, i.e., always betting with high equity (say >= 0.65), always calling for moderate (0.5 to < 0.65) and fold anything less (assuming a single opponent context) then this will get us a basic opponent that will be tough to beat initially.  In other words, we could bias the probabilities of <bet, call, fold> with starting equity and let it go from there.  This would cover our 'tight' sample behaviours.
        - tight e loose? passive e agressive?
        - This playing style is called "tight", as you are very selective and only play hands where you think you have an advantage. At a table with nine players you should only play 15 to 20 per cent of the hands you are dealt, on average. This means you should fold before the flop in four out of five cases. 
        Some opponents won't stick to this recommendation and play almost every hand, which is a style of play known as "loose".
        https://www.pokerschoolonline.com/articles/Playing-Style-and-Position
- inserir relative entropy no codigo principal
- checar o quao bem NCD e entropy diferenciam entre eles + os 3 always para 100 hands vs cada oponente (incluindo a si mesmo, e na mesma ordem para todos)
    - alterar play_match para jogar 100 hands com seed 1, e forcar para o sbb e o oponente serem coded oponentes
    obter a action sequence no final, e colocar um raise SystemExit
    - concatenar todas as action sequences daquele coded opponent
    - e automaticamente calcular e printar as distances
    - fazer isso em um script em tools, para ser um procedimento repetivel
    - I implemented entropy and is not very clear if entropy or NCD are the best options, so the next thing I will do is implement a more detailed test. First I will implement the 4 static opponents (the agressive/passive and tight/loose ones). Then I will run each opponent for 100 hands against all the 7 opponents (the 4 static ones + the 3 ''always X'' ones), get the total sequence of actions for each one and use them as inputs for the NCD and entropy algorithms. I expect that this way I will be able to find the better distance metric to obtain diversity in poker behaviors (or at least for poker behaviors that aren't super complex). Do you have any suggestions about how I should perform this test besides or regarding what I described? Maybe ensure that the 100 hands are balanced?
- fazer runs com ttt? (sem ncd?)
- implementar scripts em tools para printar os charts (violin, line, etc), python or R? conferir papers do SBB, GP e tutorials para ver os charts mais usados
- escrever report
    (com o que foi implementado (opponents, diversities, inputs...), o q pretendo implementar, resultados iniciais e charts, os parametros usados, o comportamento dos poker players, os aparentes problemas (right now they are only learning the ratio between raise and call, they dont learn to fold, and it is essential for them to learn it in order to evolve); since I can perform a lot of runs of TTT with various configurations and comapre them with U-Test, I am trying to find initial good parameters for poker this way (maybe I should use a more complex, but still quick, game for it instead?); removed always_fold opponent)

extra:
- fazer mais testes com e sem hand potential, para analisar o runtime
- repassar comentairos do paper sobre NCD para o doc
- voltar a fazer runs de ttt?
- 3 ou 4 grupos de equity e strength? 10/20/30/40 ou 20/30/50?
- ajeitar arquivos em pastas core e utils
- 10 ou 20 instructions?
------------------
extra:
- perguntar se o paper Ideal Evaluation from Coevolution foi usado como base para a point population evolution com pareto na versao original do SBB
- refatorar update_opponent_model_and_chips (baseado nos warnings)
- volatility, agressiveness, hand potential?
- memmory: parar de usar negative potential? salvar outputs em arquivo durante a execucao? nao salvar poker memory para champion?
- as metricas globais mostram os resultados considerando apenas as team parents, deveriam tambem considerar as team children?

---

future work:
- fazer versao do pSBB sem poker, para ser open source, e mover poker para um branch
- nos testes, checar se os teams sabem blefar
- refatorar codigo
- ir testando enquanto implementa:
    - (pc de casa, pc do lab (4 cores), NIMS server (6 cores), Hector, e Bluenose(?))
- intron
    if r[1] < r[1]: # AQUI
        if r[0] >= i[0]:
            if r[0] < i[0]:
                r[0] = cos(r[0])
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