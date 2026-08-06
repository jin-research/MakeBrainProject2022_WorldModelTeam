import pandas as pd

#num_for_action0_assignment = 0
#step_of_mean = 20
#action0_data = pd.Series(0)

def take_action_moving_average(action0_data, num_for_action0_assignment, action):
    action0 = pd.Series(action[0])
    print(action0)
    action0_data = pd.concat([action0_data[-step_of_mean:], action0], ignore_index=True)

    action0_mod = pd.DataFrame(action0_data).ewm(span=step_of_mean).mean().iloc[-1].tolist()[0]
    action[0] = action0_mod
    action0_data[-1:] = action0_mod
    
    return action0_data, num_for_action0_assignment, action
