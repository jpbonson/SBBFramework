/********************************************************************************************
 * Assign each team a score based on multi-objective Pareto ranking with novelty 
 * and performance as objectives
 */
void sbbModule::paretoScoreRanking(long t, long level, vector < noveltyDescriptor > &noveltyArchive){
   vector < team * > teams;
   set < team *, teamIdComp > :: iterator teiter, teiterend;

   for(teiter = _M.begin(); teiter != _M.end(); teiter++){
      teams.push_back(*teiter);
      (*teiter)->domBy(0);
      (*teiter)->domOf(0);
      (*teiter)->fitness((*teiter)->getMeanOutcome(TRAIN_REWARD,TRAIN_PHASE));
   }

   double nov_0 = 0;
   double nov_1 = 0;
   double novMin_0 = HUGE_VAL;
   double novMin_1 = HUGE_VAL;
   double novMax_0 = 0;
   double novMax_1 = 0;
   double novMean_0 = 0; //reporting only
   double novMean_1 = 0; //reporting only
   vector < distanceInstance > distances_0;
   vector < distanceInstance > distances_1;
   int numDistFromArchive = 0;
   vector <int> behaviourSequence;

   //measure novelty and fitness means w.r.t rest of population
   for(int i = 0; i < teams.size(); i++){
      //get distance w.r.t each other team
      distances_0.clear();
      distances_1.clear();
      for(int j = 0; j < teams.size(); j++){
	 if (i != j){
	    distances_0.push_back(distanceInstance(teams[i]->symbiontUtilityDistance(teams[j],_omega),false));
	    distances_1.push_back(distanceInstance(teams[i]->ncdBehaviouralDistance(teams[j]),false));
	 }
      }
      std::sort(distances_0.begin(),distances_0.end(),compareByDistance);
      std::sort(distances_1.begin(),distances_1.end(),compareByDistance);
      nov_0 = 0;
      nov_1 = 0;
      for (int k = 0; k < _knnNovelty && k < distances_0.size(); k++){//distances_0 and distances_1 will be same size
	 nov_0 += distances_0[k].distance;
	 nov_1 += distances_1[k].distance;
      }
      nov_0 = nov_0/_knnNovelty;
      nov_1 = nov_1/_knnNovelty;
      novMean_0 += nov_0;
      novMean_1 += nov_1;
      teams[i]->novelty(0,nov_0);
      teams[i]->novelty(1,nov_1);
      if (nov_0 < novMin_0)
	 novMin_0 = nov_0;
      if (nov_1 > novMax_1)
	 novMax_1 = nov_1;
   }
   oss << "scm::novStats t " << t << " l " << level << " novMin_0 " << novMin_0 << " novMin_1 " << novMin_1 << " novMax_0 " << novMax_0 << " novMax_1 " << novMax_1;
   oss << " novMean_0 " << novMean_0/teams.size() <<  " novMean_1 " << novMean_1/teams.size() << " msize " << teams.size() << " meanNumDistFromArchive " << numDistFromArchive/teams.size() << endl;

   cout << oss.str();
   oss.str("");


   /* Pareto Scoring */
   vector < team * > dominatedTeams;
   vector < team * > nonDominatedTeams;
   vector < team * > :: iterator teiterA, teiterAend;
   vector < team * > :: iterator teiterB, teiterBend;

   dominatedTeams.clear();
   nonDominatedTeams.clear();
   for(teiterA = teams.begin(); teiterA != teams.end(); teiterA++){
      for(teiterB = teams.begin(); teiterB != teams.end(); teiterB++){
	 if ((((*teiterB)->fitness() > (*teiterA)->fitness() && isEqual((*teiterA)->fitness(), (*teiterB)->fitness(), _paretoEpsilonTeam) == false) ||
		  ((*teiterB)->novelty(_hostDistanceMode) > (*teiterA)->novelty(_hostDistanceMode) && isEqual((*teiterA)->novelty(_hostDistanceMode), (*teiterB)->novelty(_hostDistanceMode), _paretoEpsilonTeam) == false)) &&
	       ((*teiterB)->fitness() >= (*teiterA)->fitness() && (*teiterB)->novelty(_hostDistanceMode) >= (*teiterA)->novelty(_hostDistanceMode))){
	    (*teiterA)->domBy((*teiterA)->domBy()+1);
	    (*teiterB)->domOf((*teiterB)->domOf()+1);
	    if(find(dominatedTeams.begin(), dominatedTeams.end(), *teiterA) == dominatedTeams.end())
	       dominatedTeams.push_back(*teiterA);
	 }
      }
      if ((*teiterA)->domBy() < 1)
	 nonDominatedTeams.push_back(*teiterA);
   }

   for(int i = 0; i < teams.size(); i++){
      teams[i]->score(1-((double)teams[i]->domBy()/teams.size()));
      //teams[i]->score((double)teams[i]->domOf()/teams.size());
   }

   //Novelty reporting
   oss.str("");
   oss.precision(10);
   oss << "sbb::paretoScoreRanking t " << t << " l " << level << " _hostDistanceMode " << _hostDistanceMode << " numFront " << nonDominatedTeams.size() << " numDom " << dominatedTeams.size() << " [id,fit,nov_0,nov_1,score] dominated ";
   for (int i = 0; i < dominatedTeams.size(); i++)
      oss <<  "[" << dominatedTeams[i]->id() << "," << dominatedTeams[i]->fitness() << "," << dominatedTeams[i]->novelty(0) << "," << dominatedTeams[i]->novelty(1) << "," << dominatedTeams[i]->score() << "] ";
   oss << " nonDominated ";
   for (int i = 0; i < nonDominatedTeams.size(); i++)
      oss << "[" << nonDominatedTeams[i]->id() << "," << nonDominatedTeams[i]->fitness() << "," << nonDominatedTeams[i]->novelty(0) << "," << nonDominatedTeams[i]->novelty(1) << "," << nonDominatedTeams[i]->score() << "] ";
   oss << endl;
   cout.precision(10);
   cout << oss.str();
   oss.str("");
}

