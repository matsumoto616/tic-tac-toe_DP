import tic_tac_toe_environment
import pickle

class Planner():
    '''
    継承元となるクラス
    ''' 
    def __init__(self, env):
        self.env = env
        self.log = []

    def initialize(self):
        self.env.reset()
        self.log = []

    def transitions_at(self, state, action, mark):
        transition_probs = self.env.transit_func(state, action, mark)
        for next_state in transition_probs:
            prob = transition_probs[next_state]
            reward, _ = self.env.reward_func(next_state)
            # yield:ジェネレータとして使用するための記述
            # for文で1つずつ値を読みだすことができる
            yield prob, next_state, reward


class ValueIterationPlanner(Planner):
    '''
    ValueIterationを行い，価値関数Vを求めるクラス
    ''' 
    def __init__(self, env):
        super().__init__(env)

    def plan(self, gamma=0.9, threshold=0.0001):
        self.initialize()
        # 価値と（取れる行動と次の状態）の組を保存する辞書
        V = {}
        # 初期化
        for s in self.env.states:
            # 勝利盤面ではvalue=1，敗北盤面ではvalue=-1，それ以外はvalue=0で初期化
            if s.status.value == self.env.player_mark:
                V[s] = 1
            elif s.status.value == self.env.player_mark * -1:
                V[s] = -1
            else:
                V[s] = 0

        # Bellman方程式を反復解法で解く
        # 価値の更新幅（の最大値）がthreshold未満になれば終了
        count = 0
        while True:
            delta = 0
            for s in V:
                # 未決着の盤面のみイタレーション（決着盤面は初期値で確定）
                if s.status == tic_tac_toe_environment.Status.UNDECIDED:
                    expected_rewards = []
                    for a in self.env.actions_available_at(s):
                        r = 0
                        for prob, next_state, reward in self.transitions_at(s, a, s.turn.value):
                            r += prob * (reward + gamma * V[next_state])
                        expected_rewards.append(r)
                    # プレイヤーの手番の時は報酬が最大となる行動が選ばれると仮定
                    if s.turn.value == self.env.player_mark:
                        max_reward = max(expected_rewards)
                        delta = max(delta, abs(max_reward - V[s]))
                        V[s] = max_reward
                    # 相手の手番の時は報酬が最小となる行動が選ばれると仮定（相手も勝ちにくるため）
                    else:
                        min_reward = min(expected_rewards)
                        delta = max(delta, abs(min_reward - V[s]))
                        V[s] = min_reward

            count += 1
            print(f'iteration {count}, delta {delta}')
            if delta < threshold:
                break

        return V

# PolicyIterationは未実装
# class PolicyIterationPlanner(Planner):

#     def __init__(self, env):
#         super().__init__(env)
#         self.policy = {}

#     def initialize(self):
#         super().initialize()
#         self.policy = {}
#         actions = self.env.actions
#         states = self.env.states
#         for s in states:
#             self.policy[s] = {}
#             for a in actions:
#                 # Initialize policy.
#                 # At first, each action is taken uniformly.
#                 self.policy[s][a] = 1 / len(actions)

#     def estimate_by_policy(self, gamma, threshold):
#         V = {}
#         for s in self.env.states:
#             # Initialize each state's expected reward.
#             V[s] = 0

#         while True:
#             delta = 0
#             for s in V:
#                 expected_rewards = []
#                 for a in self.policy[s]:
#                     action_prob = self.policy[s][a]
#                     r = 0
#                     for prob, next_state, reward in self.transitions_at(s, a):
#                         r += action_prob * prob * \
#                              (reward + gamma * V[next_state])
#                     expected_rewards.append(r)
#                 value = sum(expected_rewards)
#                 delta = max(delta, abs(value - V[s]))
#                 V[s] = value
#             if delta < threshold:
#                 break

#         return V

    # def plan(self, gamma=0.9, threshold=0.0001):
    #     self.initialize()
    #     states = self.env.states
    #     actions = self.env.actions

    #     def take_max_action(action_value_dict):
    #         return max(action_value_dict, key=action_value_dict.get)

    #     while True:
    #         update_stable = True
    #         # Estimate expected rewards under current policy.
    #         V = self.estimate_by_policy(gamma, threshold)
    #         self.log.append(self.dict_to_grid(V))

    #         for s in states:
    #             # Get an action following to the current policy.
    #             policy_action = take_max_action(self.policy[s])

    #             # Compare with other actions.
    #             action_rewards = {}
    #             for a in actions:
    #                 r = 0
    #                 for prob, next_state, reward in self.transitions_at(s, a):
    #                     r += prob * (reward + gamma * V[next_state])
    #                 action_rewards[a] = r
    #             best_action = take_max_action(action_rewards)
    #             if policy_action != best_action:
    #                 update_stable = False

    #             # Update policy (set best_action prob=1, otherwise=0 (greedy))
    #             for a in self.policy[s]:
    #                 prob = 1 if a == best_action else 0
    #                 self.policy[s][a] = prob

    #         if update_stable:
    #             # If policy isn't updated, stop iteration
    #             break

    #     # Turn dictionary to grid
    #     V_grid = self.dict_to_grid(V)
    #     return V_grid


def main(player_mark):
    plan_type = 'value'
    env = tic_tac_toe_environment.Environment(player_mark)
    # value iteration
    if plan_type == 'value':
        # value iterationで価値を求める
        planner = ValueIterationPlanner(env)
        V = planner.plan()

        # 得られた価値関数を保存
        if player_mark == 1:
            with open('V_for_CIRCLE.pkl', 'wb') as f:
                pickle.dump(V, f)
        elif player_mark == -1:
            with open('V_for_CROSS.pkl', 'wb') as f:
                pickle.dump(V, f)

    # policy iteration (未実装)
    elif plan_type == 'policy':
        planner = PolicyIterationPlanner(env)


if __name__=='__main__':
    # 先手番用のVを求める
    print('Calculating V for CIRCLE...')
    main(1)
    print('Completed')

    # 後手番用のVを求める
    print('')
    print('Calculating V for CROSS...')
    main(-1)
    print('Completed')