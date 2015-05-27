- alterar validate_action para get_valid_actions, para acelerar o run
- conferir se a amtch de tic tac toe esta funcionando corretamente
- implementar oponente com IA (https://inventwithpython.com/chapter10.html), e self-play (no self-play, cuidado para 1 == si mesmo e 2 == oponente)
- conferir se pareto e fitness sharing ainda funcionam mesmo quando a fitness sao vitorias ou dinheiro ganho (normalizar resultados?)
- refatorar environments (criar environment de reinforcement?)

- fazer testes unitarios (classe logger?)
- melhorar README.md
- fornecer examples de CONFIG
- conferir codigo c++ (se necessario)
- velocidade de rodar?
- fazer mais testes unitarios (conferir se os resultados estao realmente ok e sem bugs)
- conferir se requirement.txt funciona
- poder salvar os melhores times no formato objeto? ou como um array de sets de instructions? (para ser mais reutilizavel?)
- implementar tradutor que le o objeto do time e computa resultados?
- adicionar mais documentacao
- remover comentarios em portugues

- implementar poker environment (resetar os registers apos cada acao (ou logo antes) e point population: opponents (static, dynamic, itself), hands, positions)
- quais opponents suar para treinar? quais para validar? usar os mesmos para ambas as coisas? isn't the best opponent useful for both?
- um point contem um oponente e uma configuracao de mao? (confirir lista de inputs!)

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
- novos learners naquele time só são gerados mutacionnando outros learners daquele mesmo time (ao inves de globalmente)
- tem mutation de swap instructions
