import operator

def round_value(value, round_decimals_to = 5):
    number = float(10**round_decimals_to)
    return int(value * number) / number

def rank_teams_by_accumulative_score(list_scores, list_ids):
    previous_score = 0.0
    best_teams = {}
    for score, team_id in zip(list_scores, list_ids):
        score_improvement = score - previous_score
        if score_improvement >= 1.0:
            if team_id not in best_teams:
                best_teams[team_id] = round_value(score_improvement)
            else:
                if score_improvement > best_teams[team_id]:
                    best_teams[team_id] = round_value(score_improvement)
        previous_score = score
    rank = sorted(best_teams.items(), key=operator.itemgetter(1), reverse=True)
    return rank

def rank_teams_by_accumulative_score2(ind_scores, acc_scores, list_ids):
    if len(ind_scores) == 0:
        return []
    best_teams = {}
    # check if first score is good enough (must be better than the others by at least 1.0 point)
    for score in ind_scores:
        if (ind_scores[0] - score) > 1.0:
            best_teams[list_ids[0]] = acc_scores[0]
    # check if the other scores are good enough
    previous_score = acc_scores[0]
    for score, team_id in zip(acc_scores, list_ids):
        score_improvement = score - previous_score
        if score_improvement > 1.0:
            if team_id not in best_teams:
                best_teams[team_id] = round_value(score_improvement)
            else:
                if score_improvement > best_teams[team_id]:
                    best_teams[team_id] = round_value(score_improvement)
        previous_score = score
    # sort the best scores
    rank = sorted(best_teams.items(), key=operator.itemgetter(1), reverse=True)
    return rank

def get_highest_ranks(rank):
    best_teams = {}
    for team_id, score in rank:
        if team_id not in best_teams:
            best_teams[team_id] = score
        else:
            if score > best_teams[team_id]:
                best_teams[team_id] = score
    rank = sorted(best_teams.items(), key=operator.itemgetter(1), reverse=True)
    return rank

# scores = [187.77083, 199.9375, 204.33333, 204.9375, 206.9375, 210.59375, 210.84375, 211.63541, 212.82291, 224.67708, 224.80208, 224.80208, 224.80208, 225.63541, 225.65625, 225.65625, 225.69791, 225.69791, 225.69791, 225.69791, 225.69791, 225.69791, 225.69791, 225.71875, 225.71875, 225.71875, 225.94791, 226.28125, 232.28124, 232.69791, 232.69791, 232.80208, 232.80208, 232.90624, 232.90624, 232.90624, 232.90624, 233.80208, 233.86458, 233.86458, 233.86458, 234.16666, 234.16666, 234.60416, 234.60416, 234.79166, 235.07291, 235.26041, 235.26041, 235.46875]
# ids = ['(7173-139)', '(7658-149)', '(7259-141)', '(7459-145)', '(4111-79)', '(7691-149)', '(7113-138)', '(7655-149)', '(7462-145)', '(7687-149)', '(7644-148)', '(5858-113)', '(6001-116)', '(7100-138)', '(7122-138)', '(7510-146)', '(7367-143)', '(7363-143)', '(7579-147)', '(6052-117)', '(7645-148)', '(6371-123)', '(7308-142)', '(6680-130)', '(7654-149)', '(7445-145)', '(6817-132)', '(6571-127)', '(5794-112)', '(7636-148)', '(7562-147)', '(7053-137)', '(7314-142)', '(7503-146)', '(7373-143)', '(7607-148)', '(6868-133)', '(7318-142)', '(7618-148)', '(7453-145)', '(7697-149)', '(7292-142)', '(7617-148)', '(7135-138)', '(7567-147)', '(6888-134)', '(7685-149)', '(7646-148)', '(7523-146)', '(7666-149)']

# scores2 = [13.08333, 13.64583, 14.62499, 14.95833, 14.97916, 14.97916, 14.97916, 14.97916, 15.04166, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.08333, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.13541, 15.15625]
# ids2 = ['(6888-134)', '(7666-149)', '(7462-145)', '(7523-146)', '(7567-147)', '(7618-148)', '(7646-148)', '(7503-146)', '(4111-79)', '(7135-138)', '(7697-149)', '(6571-127)', '(7617-148)', '(7053-137)', '(7373-143)', '(7314-142)', '(6680-130)', '(7308-142)', '(7367-143)', '(7654-149)', '(7645-148)', '(6817-132)', '(7579-147)', '(7655-149)', '(7122-138)', '(7562-147)', '(7636-148)', '(6868-133)', '(5858-113)', '(6001-116)', '(7445-145)', '(7685-149)', '(6052-117)', '(7658-149)', '(6371-123)', '(7510-146)', '(7607-148)', '(7459-145)', '(7453-145)', '(7363-143)', '(7318-142)', '(7644-148)', '(7100-138)', '(7687-149)', '(7173-139)', '(7259-141)', '(7292-142)', '(7113-138)', '(7691-149)', '(5794-112)']

# a = rank_teams_by_accumulative_score(scores, ids)
# b = rank_teams_by_accumulative_score(scores2, ids2)
# print str(a)
# print
# print str(a+b)
# print
# print str(sorted((a+b), key=operator.itemgetter(1), reverse=True))
# print
# print str(a+b+b)
# print
# c = sorted((a+[('(6888-134)', 100505.5)]+b+b+[('(6888-134)', 10005.5)]), key=operator.itemgetter(1), reverse=True)
# print str(c)
# print
# print str(get_highest_ranks(c))

inds = [13.08333, 13.07291, 11.85416]
scores2 = [13.08333, 13.64583, 15.62499]
ids2 = ['(6888-134)', '(7666-149)', '(7462-145)']
b = rank_teams_by_accumulative_score2(inds, scores2, ids2)
print str(b)


# o primeiro deve ser melhor em 1.0 em relacao a ao menos um dos outros scores?