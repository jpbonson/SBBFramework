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
100-50-200 (ok)
200-100-100 (ok)
200-100-200 (ok)
100-50-200 (with 2 registers) (ok)
100-50-400 (ok)
100-50-200 (repl0.3) (ok)
100-50-200 (action0.1) (ok)
100-50-200 (10/30 programs) (ok)

100-50-200 > 200-100-100: 0.03156
100-50-200 == 100-50-400: The Z-Score is -0.2522. The p-value is 0.80258. (mean == mean) ????????????
200-100-100 < 200-100-200: 0.03156
100-50-400 == 200-100-200: The Z-Score is 0.291. The p-value is 0.77182. (mean == mean)
100-50-200 (with 1 registers) == 100-50-200 (with 2 registers): The Z-Score is 1.6201. The p-value is 0.10524. (mean > mean)
100-50-200 (repl0.2) == 100-50-200 (repl0.3): The Z-Score is 1.2612. The p-value is 0.20766. (mean > mean)
100-50-200 (action0.3) ? 100-50-200 (action0.1): The Z-Score is -0.097. The p-value is 0.92034. (mean == mean)
100-50-200 (10/20 programs) ? 100-50-200 (10/30 programs): The Z-Score is 1.3582. The p-value is 0.17384. (mean > mean)

resultado:
100-50-200, with 1 registers, repl0.2, action0.1, 10/30 programs

duvida: nao melhorou com mais generations?

120-60-200 == 100-50-200: The Z-Score is -0.7567. The p-value is 0.44726. (mean > mean)
160-80-200 == 100-50-200: The Z-Score is 0.9507. The p-value is 0.34212. (mean < mean)
160-80-200 == 200-100-100: The Z-Score is 1.0284. The p-value is 0.30302. (mean> mean)
120-60-200 == 160-80-200: The Z-Score is 1.7075. The p-value is 0.08726. (mean > mean)
120-60-200 == 120-60-400: The Z-Score is -1.106. The p-value is 0.267. (mean < mean)
160-80-200 < 160-80-400: 0.02444
120-60-400 == 160-80-400: The Z-Score is 0.1843. The p-value is 0.85716. (mean == mean)
------------------- winner: 160-80-200

Results (Thyroid):

default == fitness sharing: The Z-Score is 1.4552. The p-value is 0.1443.
default == cw fitness sharing: The Z-Score is 1.2127. The p-value is 0.22628.
default == genotype01: The Z-Score is -1.2709. The p-value is 0.20408.
default == genotype02: The Z-Score is 0.553. The p-value is 0.58232.
default == genotype03: The Z-Score is 0.1649. The p-value is 0.87288.
genotype01 == genotype03: The Z-Score is 1.3194. The p-value is 0.18684.
genotype01 == genotype02: The Z-Score is 1.4649. The p-value is 0.1443.
genotype01 venceu (entre genotypes)
+ runs

default == complex: The Z-Score is 1.1254. The p-value is 0.25848.

default ? no introns (rerodar)
complex ? complex + no introns (rerodar)
intorns realmente aceleram?

DONE:
pre-tuning < no balance: The Z-Score is -4.5112. The p-value is 0. The result is significant at p≤ 0.05. The U-value is 79.5.
no balance == default: The Z-Score is 0.2619. The p-value is 0.79486. The U-value is 298.5.
pre-tuning ? default: The Z-Score is -5.0641. The p-value is 0. The result is significant at p≤ 0.01. The U-value is 51
OK: Various modifications were made from the previous runs to try to improve the results. The point replacement rate was changed from 1.0 to 0.2, the populations from 400/200 to 160/80, the generations from 20 to 500, and balance restrictions were added, to ensure that all teams always have at least of action per class. The most impactful change was the modification of the generation and populations. The best solution across 25 runs was 0.94206 for the Thyroid dataset. The new best solution is 0.97135. The distribution of results improved with significance at p≤ 0.01 with the Mann-Whitney U-Test. The modification of the point replacement rate and the balance restrictions didn't significantly imprvoed the results, but were maintained in order to ensure the best functioning of the algorithm.

------------------------------

Results (Shuttle):



TODO:
- rodar benchmarks para thyroid
- rodar com e sem as melhorias
- rodar benchmarks para shuttle (fazer mais runs? 50? sets de 10? no server?)
- rodar introns e complex
- rodar diversities