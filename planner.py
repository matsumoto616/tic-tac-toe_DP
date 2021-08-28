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
                if s.status != tic_tac_toe_environment.Status.UNDECIDED:
                    continue

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

class PolicyIterationPlanner(Planner):

    def __init__(self, env):
        super().__init__(env)
        self.policy = {}

    def initialize(self):
        super().initialize()
        self.policy = {}
        states = self.env.states
        # 戦略の初期化。初期の行動確率は平等にする
        for s in states:
            # 未決着の盤面のみpolicyを求める
            if s.status != tic_tac_toe_environment.Status.UNDECIDED:
                continue
            self.policy[s] = {}
            for a in self.env.actions_available_at(s):
                self.policy[s][a] = 1 / len(self.env.actions_available_at(s))

    def estimate_by_policy(self, gamma, threshold):
        V = {}
        # 価値Vを初期化
        for s in self.env.states:
            # 勝利盤面ではvalue=1，敗北盤面ではvalue=-1，それ以外はvalue=0で初期化
            if s.status.value == self.env.player_mark:
                V[s] = 1
            elif s.status.value == self.env.player_mark * -1:
                V[s] = -1
            else:
                V[s] = 0

        count = 0
        while True:
            delta = 0
            for s in V:
                # 未決着の盤面のみイタレーション（決着盤面は初期値で確定）
                if s.status != tic_tac_toe_environment.Status.UNDECIDED:
                    continue

                expected_rewards = []
                for a in self.policy[s]:
                    action_prob = self.policy[s][a]
                    r = 0
                    for prob, next_state, reward in self.transitions_at(s, a, s.turn.value):
                        r += action_prob * prob * \
                            (reward + gamma * V[next_state])                          
                    expected_rewards.append(r)
                value = sum(expected_rewards)
                delta = max(delta, abs(value - V[s]))
                V[s] = value
            
            count += 1
            print(f'    Value iteration {count}, delta {delta}')
            if delta < threshold:
                break

        return V

    def plan(self, gamma=0.9, threshold=0.0001):
        self.initialize()
        states = self.env.states

        def take_max_action(action_value_dict):
            return max(action_value_dict, key=action_value_dict.get)

        def take_min_action(action_value_dict):
            return min(action_value_dict, key=action_value_dict.get)

        count = 0
        while True:
            count += 1
            print(f'Policy iteration {count}')

            update_stable = True
            # 現在の戦略のもとでVをValueIterationで求める
            V = self.estimate_by_policy(gamma, threshold)

            for s in states:
                # 未決着の盤面のみ考える
                if s.status != tic_tac_toe_environment.Status.UNDECIDED:
                    continue

                # 現在の戦略において，状態sのもとでの行動価値が最も高い行動を取り出す
                policy_action = take_max_action(self.policy[s])

                # 他の行動を取った場合の報酬も求めて比較する
                action_rewards = {}
                for a in self.env.actions_available_at(s):
                    r = 0
                    for prob, next_state, reward in self.transitions_at(s, a, s.turn.value):
                        r += prob * (reward + gamma * V[next_state])
                    action_rewards[a] = r
                
                # プレイヤーの手番の場合は一番報酬が高い行動がベスト
                if s.turn.value == self.env.player_mark:
                    best_action = take_max_action(action_rewards)
                # 相手の手番の場合は一番報酬が低い行動が選ばれるとする
                # （相手も勝ちに来るため）
                else:
                    best_action = take_min_action(action_rewards)

                # 戦略が導きだす行動が他の行動候補と比較してベストな洗濯であればOK
                # そうでなければupdate_stable=Falseとしてイタレーション
                if policy_action != best_action:
                    update_stable = False

                # 価値最大の行動を戦略がとるように反映
                # ここではbest_actionの確率を1，それ以外を0とする（貪欲法）
                for a in self.policy[s]:
                    prob = 1 if a == best_action else 0
                    self.policy[s][a] = prob

            # 戦略がとる行動が安定すれば終了
            if update_stable:
                break

        return self.policy


def main(player_mark, plan_type):
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

    # policy iteration
    elif plan_type == 'policy':
        # policy iterationで戦略を求める
        planner = PolicyIterationPlanner(env)
        policy = planner.plan()

        # 得られた戦略を保存
        if player_mark == 1:
            with open('policy_for_CIRCLE.pkl', 'wb') as f:
                pickle.dump(policy, f)
        elif player_mark == -1:
            with open('policy_for_CROSS.pkl', 'wb') as f:
                pickle.dump(policy, f)


if __name__=='__main__':
    # Value Iteration
    # 先手番用のVを求める
    print('Calculating V for CIRCLE...')
    main(1, 'value')
    print('Completed')

    # 後手番用のVを求める
    print('')
    print('Calculating V for CROSS...')
    main(-1, 'value')
    print('Completed')

    # Policy Iteration
    # 先手番用のpolicyを求める
    print('')
    print('Calculating policy for CIRCLE...')
    main(1, 'policy')
    print('Completed')

    # 後手番用のpolicyを求める
    print('')
    print('Calculating policy for CROSS...')
    main(-1, 'policy')
    print('Completed')