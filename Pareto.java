- implementar pareto front com fitness sharing para points
- remover referencias aos points qd eles sao removidos da population?
- conferir se pareto e fitness sharing ainda funcionam mesmo quando a fitness sao vitorias ou dinheiro ganho (normalizar resultados?)

- conferir codigo c++ (se necessario)
- velocidade de rodar?
- fazer testes unitarios
- conferir se os resultados estao realmente ok e sem bugs
- conferir se requirement.txt funciona
- identar ifs nas instructions?
- poder salvar os melhores times no formato objeto? ou como um array de sets de instructions? (para ser mais reutilizavel?)
- implementar tradutor que le o objeto do time e computa resultados?
- adicionar mais documentacao
- remover comentarios em portugues
- classe logger?

- implementar reinforcement learning para tictactoe
- implementar poker environment (resetar os registers apos cada acao (ou logo antes) e point population: opponents (static, dynamic, itself), hands, positions)

Observacoes:
- cada dimensao da point population eh uma das dimensoes q vai ser maximizada no pareto, gerando as poker behaviors
- cycling. disingagement, overspecialization, forgetting
- hall of fame

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

// adicionar outputs para pointFrontSize e teamFrontSize
// store only outcomes from the current point population! (to avoid too much memory usage)

/* CURRENTLY THE SHARING SCORE CALCULATION IS OK BECAUSE EACH
DIMENSION IS EITHER 0 OR 1. IF THE DIMENSIONS CAN TAKE ON
DIFFERENT RANGES, MAY NEED TO NORMALIZE (THIS ASSUMES THAT EACH
DIMENSION RECEIVES THE SAME WEIGHTING). */

    public void selection( long t )
    {
        if selecting_team:
            population = M
        else:
            population = P
                     
        // Stores the teams to remove
        ArrayList<Team> toDel = new ArrayList<Team>();
               
        // Number of teams that make it to the next generation
        if selecting_team:
            int keep = Msize - Mgap;
        else:
            int keep = Psize - Pgap;
             
        if selecting_team:  
            HashMap<Team, ArrayList<Double>> outMap = // a matrix of (teams) x (array of outcomes for each point, just for the current point population)
        else:
            // trying to get points that are selecting distinct teams
            // using Pareto for the point population isn't favouring points that are easy to guess?
            HashMap<Point, ArrayList<Short>> outMap = // a matrix of (points) x (array version of a matrix that compares all teams outcomes against each other for this point  (0: <=, 1: >))

        // Get the Pareto front
        front, dominateds = findParetoFront( outMap);
        
        if( front.size() == keep )
        {
            toDel = dominateds;
        }
        else if( front.size() < keep ) // Must include some teams from dominateds
        {
            fitness_sharing_score = sharingScore( outMap, dominateds, population );
            nrem = dominateds.size() - (keep - front.size()); // Number of teams to remove
            toDel = // get the 'nrem' teams from 'dominateds' with the lower 'fitness_sharing_score'
        }
        else // Must discard some teams from front
        {
            fitness_sharing_score = sharingScore( outMap, front, front );
            nrem = front.size() - keep; // Number of teams to remove
            toDel = // get the 'front' teams from 'dominateds' with the lower 'fitness_sharing_score'
            
            // After selPareto toDel contains teams from front to be deleted; must add all teams from dominateds to toDel
            toDel.addAll( dominateds );
        }

        return toDel
    }