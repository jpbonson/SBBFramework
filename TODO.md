- conferir se np.iinfo(np.int32).max no Ubuntu == 2147483647
    >>> sys.maxint: 9223372036854775807 (ubuntu) e 2147483647 (windows e np.iinfo(np.int32).max)

- implementar hall of fame [true, false]
- fazer system test para tictactoe (hall of fame)
- ler paper sobre tictactoe
- fazer example para tictactoe

---
- fazer example para thyroid

- conferir se pareto e fitness sharing ainda funcionam mesmo quando a fitness sao vitorias ou dinheiro ganho (normalizar resultados?)
- implementar poker environment (resetar os registers apos cada acao (ou logo antes) e point population: opponents (static, dynamic, itself), hands, positions), um point inclui a position, ou todos os points sempre incluem varias matches em todas as positions?
- refatorar environments (criar environment de reinforcement?)

- experimentar violin plot na R language (our usar http://matplotlib.org/examples/statistics/violinplot_demo.html e integrar no pSBB)
- usar import logging para nao floodar a tela com prints qd um test falhar
- melhorar README.md
- velocidade de rodar?
- fazer mais testes unitarios (conferir se os resultados estao realmente ok e sem bugs)
- conferir se requirement.txt funciona
- poder salvar os melhores times no formato objeto? ou como um array de sets de instructions? (para ser mais reutilizavel?)
- implementar tradutor que le o objeto do time e computa resultados?
- adicionar mais documentacao
- remover comentarios em portugues

---

Observacoes:
- cada dimensao da point population eh uma das dimensoes q vai ser maximizada no pareto, gerando as poker behaviors
- cycling. disingagement, overspecialization, forgetting
- hall of fame
- Reward for point population:
    - Distinctions: reward tests for every pair of solutions they distinguish
    - Informativeness: reward tests for unique partitioning of S

Guidelines:
- usar apenas um _ no methods
- usar _ no final dos atributos internos (que nao vieram de parametros)

jSBB:
- teams always start with 2 learners
- programsize = aleatorio entre 1 e 48
- mutation de programas: add, remove, swap e change_instruction
- outras diferenças entre a implementação java: tratamento para overflow (usar valor anterior vs zerar), if (ser um if memso vs mudar o sinal do regsitrador)
- se children tiverem os mesmos learners que os parents, obriga a mutacionar
- novos learners naquele time só são gerados mutacionando outros learners daquele mesmo time (ao inves de globalmente)
- tem mutation de swap instructions

========
NOTES:

solutions: local, global, historical, end goal: global

- across runs, use the same validation and champion set, or generate new random sets for each run? (?)
    - by now, generate new ones for each run, in order to cover more settings of points

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

- implementar self-play ['only_sbb', 'only_coded_opponents', 'hybrid']
    - encapsular teams em points (mas nao avaliar esses points em evaluate, novos points devem ser obtidos a cada generation da population atual)
    - alterar metodos que modificam point_population_ de acordo
    - selecionar teams com uniform probability? com weighted? (usando: weighted)
    - validation and champion population never use sbb_opponents (so they are always the same across runs)

- improves self-play so the opponent sbb also improves its metrics? (just set is_training to True?) (is it worth to fix it? for the sbb opponent, it will seem as if the point population is much larger)
    - daria para habilitar que ambos os teams no modo self_play only atualizassem suas metrics com as matches se nem pareto e nem fitness sharing forem utilizados

Notes from meeting with Malcolm:

- sempre usar todos os opponents no training e na validation, nao apenas os fortes (senao pode ocorrer do SBB aprender a vencer 
apenas de oponentes fortes, e perder quando enfrentar os fracos)

- Final output of SBB runs:
    - best solution for every run (find them using the whole validation set in the last generation)
    - distribution of the results for the best solutions of each run (for scores, also for diversities?), using violin chart (R language)

- Como obter various poker playing behaviors? (all options using the validation set)
    - get the best ones per run, focusing in which opponents they are able to beat
    - apply pareto to try to obtain a diverse front
    - use a second layer (hierarquical SBB) to let SBB itself decide it