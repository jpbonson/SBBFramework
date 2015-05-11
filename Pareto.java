- fazer mapping das actions para numeros

- cofnerir codigo c++
- preparar github
- refatorar codigo do sandbox



- cada dimensao da point population eh uma das dimensoes q vai ser maximizada no pareto, gerando as poker behaviors


mandar email para Malcolm? perguntar sobre github?

conferir codigo em C++

- usar um random number generator:
RNG = new Random( Integer.valueOf(arguments.get("seed")) ); (opcional)

- criar point population (uma classe Point)
- the point id should be the index of the point in this vector

- conferir se esta compativel com os parametros do jSBB

- implementar pareto front (conferir distanceToSqrd em Team)

- conferir se os resultados estao realmente ok e sem bugs

- fazer testes unitarios

-velocidade de rodar?

- consertar gambi de label -1
-consertar toString()

- remover fitness sharing? e outras coisas opcionais?

- teams always start with 2 learners
- programsize = aleatorio entre 1 e 48

- salvar os resultados obtidos para os points, para reaproveita-los se os mesmos points reaparecerem

- instructions: +, -, *, /, cos, log, exp, if(dest < source)

- conferir se a function está funcionando assim: 1 / (1 + Math.exp( -run( bid, feature, dim, REG )));

- melhorar codigo do Operator (fazer tratamento comum a todos no final)

- mutation de programas: add, remove, swap e change_instruction

- reinforcement learning idea:

public double evaluate( Team team, Point point )
    {
        double rewardSum = 0;
        long action;

        // Get initial state defined by point
        ArrayList<Double> state = point.getState();
        
        OpenBoolean end = new OpenBoolean(false);
                
        while( end.getValue() == false )
        {
            action = team.getAction( state );
            rewardSum += act( point, action, state, end );
        }

        return rewardSum;
    }
    
    // Act given the (starting) point, action, and (current) state. Return
    // rewards and write whether or not end state has been reached.
    public double act( Point point, long action, ArrayList<Double> state, OpenBoolean end )
    {
        end.setValue(true);
        
        if( point.getLabel() == getLabel(action) )
          return 1.0;
        else
          return 0.0;
    }

- outras diferenças entre a implementação java: tratamento para overflow (usar valor anterior vs zerar), if (ser um if memso vs mudar o sinal do regsitrador)
- se children iverem os mesmos learners que os parents, obriga a mutacionar
- novos learners naquele time só são gerados mutacionnando outros learners daquele mesmo time (ao inves de globalmente)

package sbbj_fast;

import java.util.*;

// adicionar outputs para pointFrontSize e teamFrontSize
// store only outcomes from the current point population! (to avoid too much memory usage)

public class SCM
{
    public void go()
    {
        // initialize point population
        // initialize team population
        
        // evaluate initial set of teams
        for( Point point : P )
            for( Team team : M )
                evaluate( team, point );
        
        // Main Loop
        for( t=0; t < this.t; t++ )
        {
            genPoints(t);
            genTeams(t);
            
            for( Point point : P )
                for( Team team : M )
                    if( point.getGTime() == t || team.getGTime() == t )
                        evaluate( team, point );
            
            // Select members into the next generation
            toDel_points = selection(t, selecting_team=false);
            toDel_teams = selection(t, selecting_team=true);

            // Delete points from toDel_points from the population (along with its references in teams)
            // Delete teams from toDel_teams from the population (along with its references in points)
        }
        
        // test and print results
    }

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
            HashMap<Team, ArrayList<Double>> outMap = // a matrix of (teams) x (array of outcomes for each point)
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

    // Pareto dominance: Given a set of objectives, a solution is said to Pareto dominate another if the first is not inferior to the second in all objectives, and, additionally, there is at least one objective where it is better.

    public void findParetoFront( HashMap<Team, ArrayList<Double>> vecMap)
    {
        // vecMap = a matrix of (teams) x (array of outcomes for each point)
        
        front = []
        dominateds = []
        i = 0
        for team1, outcomes1 in vecMap:
            is_dominated = false;
            j = 0
            for team2, outcomes2 in vecMap:
                is_dominated, is_equal = is_dominated( outcomes1, outcomes2 );
                if j < i and is_equal: // Also dominated if equal to a previous processed item, since this one would be irrelevant
                    is_dominated = true
                if is_dominated:
                    break
                j++
            if is_dominated:
                dominateds.append(team1)
            else:
                front.append(team1)
            i++
        return front, dominateds
    }
    
    // Assume higher outcomes are better.
    public boolean is_dominated( ArrayList<Double> team_outcomes1, ArrayList<Double> team_outcomes2) 
    {       
        epsilon = 0.1
        equal = true      
        for( int i=0; i < team_outcomes1.size(); i++ )
        {
            if( Math.abs(team_outcomes1.get(i) - team_outcomes2.get(i)) > epsilon ) { // if they are not basically equal in this dimension
                equal = false
                if( team_outcomes1.get(i) > team_outcomes2.get(i) ) // Not dominated since "team_outcomes1" is greater than "team_outcomes2" in this dimension
                    return false, equal;
            }
        }

        if equal:
            return false, equal
        else:
            return true, equal
    }
        
    public void sharingScore( HashMap<Team, ArrayList<Double>> outMap, ArrayList<Team> forThese, ArrayList<Team> wrtThese )
    {   
        HashMap<Team, Double> score;

        // Denominator in each dimension
        ArrayList<Double> nd = new ArrayList<Double>();
        
        int outvecsize = outMap.get( outMap.keySet().iterator().next() ).size();
        
        // Initialize to 1 so we don't divide by zero
        for( int s=0; s < outvecsize; s++ )
            nd.add( 1.0 ); // ?
        
        // Calculate denominators in each dimension
        for( Team team : wrtThese )
        {
            outvec = outMap.get(team);
            for( int i=0; i < outvecsize; i++ )
                nd.set(i, (double)(nd.get(i) + outvec.get(i)));         
        }
        
        for( Team team : forThese )
        {
            outvec = outMap.get(team);
            sc = 0.0;
            
            for( int i=0; i < outvecsize; i++ )
                sc += ((double) outvec.get(i) / nd.get(i));
            
            score.put( team, sc ); // dividir sc pelo total? ou nem vale a pena por dar numeros muito pequenos?
        }
        return score
    }
}
