- fazer CONFIG poder ser editavel nos tests
- implementar CONFIGs default de exemplo (e test cases), apenas para classification?
- usar import logging para nao floodar a tela com prints qd um test falhar

- Metrics:
    - diversity (calculate the average distance between all pairs (focusing in a point. or in the whole population))
    - mostrar as distributions necessarios para fazer o grafico de violao

- Tictactoe:
    - point population: opponent, position and seed (como setar a seed para apenas uma match? resetar para a seed original apos a match?)
    - use point population and replacement of points
    - team size: 20

- Reinforcement learning:
    - during training, execute few matches (10?)
    - after some generations (and at the first one), validate (generation 250?) by doing all the teams (or just the pareto 
    front? or just the parents?) play matches (100?) against all the training point population, obtaining a champion. Then this 
    champion playes more matches (1000?) to obtain the final results.
    - sempre usar todos os opponents no training e na validation, nao apenas os fortes (senao pode ocorrer do SBB aprender a vencer 
    apenas de oponentes fortes, e perder quando enfrentar os fracos)
    - mostrar taxas de vitoria contra cada oponente


---
- alterar validate_action para get_valid_actions, para acelerar o run
- conferir se a match de tic tac toe esta funcionando corretamente
- implementar oponente com IA (https://inventwithpython.com/chapter10.html)
- conferir anotacoes da reuniao com o Malcolm
- implementar self-play (no self-play, cuidado para 1 == si mesmo e 2 == oponente)
- conferir se pareto e fitness sharing ainda funcionam mesmo quando a fitness sao vitorias ou dinheiro ganho (normalizar resultados?)
- refatorar environments (criar environment de reinforcement?)

- fazer testes unitarios
- melhorar README.md
- fornecer examples de CONFIG
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
- novos learners naquele time só são gerados mutacionando outros learners daquele mesmo time (ao inves de globalmente)
- tem mutation de swap instructions



Notes from meeting with Malcolm:

- Final output of SBB runs:
    - best solution for every run (find them using the whole validation set in the last generation)
    - distribution of the results for the best solutions of each run

- Como obter various poker playing behaviors? (all options using the validation set)
    - get the best ones per run, focusing in which opponents they are able to beat
    - apply pareto to try to obtain a diverse front
    - use a second layer (hierarquical SBB) to let SBB itself decide it