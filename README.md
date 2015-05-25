# GeneticProgramming

To run all tests, execute in the main folder:
nosetests

You can also execute individual tests files regurlarly using the file name:
python tests/unit_tests/unit_tests.py


# TASK LIST:
- identar ifs nas instructions?
- como escolher melhor pareto front entre runs
- criar nova release v0

- implementar reinforcement learning para tictactoe
- conferir se pareto e fitness sharing ainda funcionam mesmo quando a fitness sao vitorias ou dinheiro ganho (normalizar resultados?)
- refatorar environments

- fazer testes unitarios (classe logger?)
- conferir codigo c++ (se necessario)
- velocidade de rodar?
- fazer mais testes unitarios (conferir se os resultados estao realmente ok e sem bugs)
- conferir se requirement.txt funciona
- poder salvar os melhores times no formato objeto? ou como um array de sets de instructions? (para ser mais reutilizavel?)
- implementar tradutor que le o objeto do time e computa resultados?
- adicionar mais documentacao
- remover comentarios em portugues

- implementar poker environment (resetar os registers apos cada acao (ou logo antes) e point population: opponents (static, dynamic, itself), hands, positions)

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
