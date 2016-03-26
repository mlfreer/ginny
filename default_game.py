def define_variables(*args, **kwargs):
    init_pts = random.randint(490, 510)
    return {'init_pts': init_pts, 'pts': init_pts}

def calculate_variables(old_variables, actions, gamer_id, *args, **kwargs):
    min_benefit_Y = 10
    max_benefit_Y = 15
    cost = {'Action X': 0, 'Action Y': 30}
    switch_cost = 20
    number_of_gamers = kwargs['number_of_gamers']
    current_round = kwargs['current_round']
    new_variables = old_variables.copy()
    action_Y_num = len(actions[-1]['by_action']['action']['Action Y'])
    action_Y_share = action_Y_num / number_of_gamers
    action_switched = current_round > 0 \
    	and actions[-1]['by_gamer'][gamer_id]['action'] == 'Action X' \
        and actions[-2]['by_gamer'][gamer_id]['action'] == 'Action Y'
    new_variables['pts'] -= cost[actions[-1]['by_gamer'][gamer_id]['action']]
    if actions[-1]['by_gamer'][gamer_id]['action'] == 'Action Y':
        benefit = min_benefit_Y if action_Y_share <= 0.5 else max_benefit_Y
        new_variables['pts'] += action_Y_num * benefit
    if action_switched:
        new_variables['pts'] -= switch_cost
    return new_variables

def is_next_round(current_round, *args, **kwargs):
	return current_round < 1 or random.randint(1, 6) < 6

def show_variables(old_variables, new_variables, actions, *args, **kwargs):
    action_Y_num = len(actions[-1]['by_action']['action']['Action Y'])
    return ["{} group member{} chose Action Y in this round"
            .format(action_Y_num, "s" if action_Y_num > 1 else ""),
           "You earned {} points in this round".format(new_variables['pts'] - old_variables['pts']),
           "You now have {} points".format(new_variables['pts'])]