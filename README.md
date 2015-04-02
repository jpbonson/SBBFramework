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
- expectitativa: melhor DR, ja que evita os local minimuns
- atualizar report
- ler paper do SBB

Obs.:
- nao tentar implementar crossover
- testar pareto com age? testar multi-objective?