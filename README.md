# GeneticProgramming

Para usar no Windows, com o Anaconda:
python "C:\Users\jpbonson\Dropbox\Dalhousie Winter 2015\Genetic Algorithms\GeneticProgrammingSandbox\main.py"
E para acessar o Git:
cd "C:\Users\jpbonson\Dropbox\Dalhousie Winter 2015\Genetic Algorithms\GeneticProgrammingSandbox"

Quando mudar de SO, mudar a variavel CURRENT_DIR

#########

TASKS:
- OK: ver parametros usados no paper do sandbox 3
- OK: testar se sistema ainda funciona ok para Thyroid, testar tudo abaixo usando Thyroid
- OK: testar qual o valor minimo de runs para o non-parametric test ser efetivoB
- OK: fazer benchmarks de datasets sem as mudancas
- OK: novos parametros (para todos os datasets):
    - sampling: 120
    - runs: 25
    - replacement% for teams: 60%
    - chance de action mudar: 0.1
    - sempre mutationar o programa clonado
    - replacement% for points: 20% (30%?)

- TODO (testar com thyroid):
    - teams: 120 / programs: 240
    - generations: 1000 (no minimo 500, se possivel, tentar mais)
    - max program size: 48? 20?
    - max programs per team: 10? 12? (mais apenas para shuttle?)

- OK:
- fix samples: samples size 120 + balanced (usar oversampling/replication)
- fix: separar chances de mutations no time entre add e remove
- fix? taxa de mutations: taxa de adds deve ser maior que remocao (por time)
- fix dynamic between PP and teams (PP repl% menor que x3 times teams repl%): substituir apenas 20% dos samples por generation, usando uniform probability + aumentar replacement da population de teams para 60%
- inicializar cada team tendo pelo menos um de cada classe

- TODO:
- achar parametros com bom resultado e runtime aceitavel (usar thyroid?)
- rerodar os testes com diversity (no modo sem diversity, rodar do modo que recalcula a fitness de todos a cada generation)
- expectativa: o grafico de DRs per class nao e mais para ter mudancas bruscas
- expectativa: melhor DR, ja que evita os local minimuns
- atualizar report
- ler paper do SBB

Obs.:
- nao tentar implementar crossover
- testar pareto com age? testar multi-objective?

Results (with bug were all new program had action 0):
200-100-100 (178) > 200-100-300 (694): 2.1731 (overfitting? mostrar training error!)
200-100-100 (178) > 100-50-100 (98): 3.153
100-50-100 (98) < 100-50-200 (963?): -3.2597
100-50-200 (963?) > 100-50-300 (417?): 2.5418
100-50-200 (678) == 200-100-100 (476) == 50-25-500 (1105)
melhor runtime: 200-100-100

-------------------
Results (with another bug were all new program had action 0):
200-100-100 (203) - 100-50-200 (273) - 200-100-200 (410) - 100-50-400 (542) ('balanced_team_mutation': True)
200-100-100 < 200-100-200
200-100-100 == 100-50-200
100-50-200 == 100-50-400

200-100-100 (with balanced mutation) == 200-100-100 (without balanced mutation): with balanced mutation
200-100-100 (with point repl0.3) == 200-100-100 (with point repl0.2): with point repl0.2

100-50-200 (10/20 programs) == 100-50-200 (24/48 programs): 10/20 programs (24/48 levou tempo demais)
100-50-200 (with point repl0.3) == 100-50-200 (with point repl0.2): repl0.2
100-50-200 (with action0.1) == 100-50-200 (with action0.3): action0.3

-------------------
Results:
100-50-200 - 200-100-100 - 100-50-400 - 200-100-200

10/20 programs e 15/30 programse 10/30 programs

with point repl0.3 e with point repl0.2

with action0.1 and with action0.3

with 1 extra register and with 2 extra registers

mutation rates?


fixed another bug with mutation always adding programs with action 0

TODO:
- rerodar experimentos que nao houve diferenca (+ register extra)
- definir parametros
- rodar benchmarks (+rodar no server, com mais generations)
- rodar intros e complex
- rodar diversities