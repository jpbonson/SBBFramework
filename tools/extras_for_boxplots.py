data['trained_against_bayes']['all_balanced'] = {
    'individual_values': 
        data['trained_against_bayes']['LA_balanced']['individual_values'] + 
        data['trained_against_bayes']['LP_balanced']['individual_values'] + 
        data['trained_against_bayes']['TA_balanced']['individual_values'] + 
        data['trained_against_bayes']['TP_balanced']['individual_values'],
    'acc_values':
        data['trained_against_bayes']['LA_balanced']['acc_values'] + 
        data['trained_against_bayes']['LP_balanced']['acc_values'] + 
        data['trained_against_bayes']['TA_balanced']['acc_values'] + 
        data['trained_against_bayes']['TP_balanced']['acc_values']
}

data['trained_against_bayes']['all_unbalanced'] = {
    'individual_values': 
        data['trained_against_bayes']['LA_unbalanced']['individual_values'] + 
        data['trained_against_bayes']['LP_unbalanced']['individual_values'] + 
        data['trained_against_bayes']['TA_unbalanced']['individual_values'] + 
        data['trained_against_bayes']['TP_unbalanced']['individual_values'],
    'acc_values':
        data['trained_against_bayes']['LA_unbalanced']['acc_values'] + 
        data['trained_against_bayes']['LP_unbalanced']['acc_values'] + 
        data['trained_against_bayes']['TA_unbalanced']['acc_values'] + 
        data['trained_against_bayes']['TP_unbalanced']['acc_values']
}

data['not_trained_against_bayes']['all_balanced'] = {
    'individual_values': 
        data['not_trained_against_bayes']['LA_balanced']['individual_values'] + 
        data['not_trained_against_bayes']['LP_balanced']['individual_values'] + 
        data['not_trained_against_bayes']['TA_balanced']['individual_values'] + 
        data['not_trained_against_bayes']['TP_balanced']['individual_values'],
    'acc_values':
        data['not_trained_against_bayes']['LA_balanced']['acc_values'] + 
        data['not_trained_against_bayes']['LP_balanced']['acc_values'] + 
        data['not_trained_against_bayes']['TA_balanced']['acc_values'] + 
        data['not_trained_against_bayes']['TP_balanced']['acc_values']
}

data['not_trained_against_bayes']['all_unbalanced'] = {
    'individual_values': 
        data['not_trained_against_bayes']['LA_unbalanced']['individual_values'] + 
        data['not_trained_against_bayes']['LP_unbalanced']['individual_values'] + 
        data['not_trained_against_bayes']['TA_unbalanced']['individual_values'] + 
        data['not_trained_against_bayes']['TP_unbalanced']['individual_values'],
    'acc_values':
        data['not_trained_against_bayes']['LA_unbalanced']['acc_values'] + 
        data['not_trained_against_bayes']['LP_unbalanced']['acc_values'] + 
        data['not_trained_against_bayes']['TA_unbalanced']['acc_values'] + 
        data['not_trained_against_bayes']['TP_unbalanced']['acc_values']
}

lines['all_balanced'] = {
    'random_opp': np.mean([lines['LA_balanced']['random_opp'], lines['LP_balanced']['random_opp'],
                lines['TA_balanced']['random_opp'], lines['TP_balanced']['random_opp']]),
    'bayes_opp': np.mean([lines['LA_balanced']['bayes_opp'], lines['LP_balanced']['bayes_opp'],
            lines['TA_balanced']['bayes_opp'], lines['TP_balanced']['bayes_opp']]),
}
lines['all_unbalanced'] = {
    'random_opp': np.mean([lines['LA_unbalanced']['random_opp'], lines['LP_unbalanced']['random_opp'],
                lines['TA_unbalanced']['random_opp'], lines['TP_unbalanced']['random_opp']]),
    'bayes_opp': np.mean([lines['LA_unbalanced']['bayes_opp'], lines['LP_unbalanced']['bayes_opp'],
            lines['TA_unbalanced']['bayes_opp'], lines['TP_unbalanced']['bayes_opp']]),
}