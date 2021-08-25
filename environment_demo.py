import random
import pickle
import sys
import numpy as np
import copy
import tic_tac_toe_environment

class InputAgent():
    '''
    標準入力で入力した行動をとるエージェント
    '''
    def __init__(self, player_mark):
        self.player_mark = player_mark

    def observe(self, env):
        action_candidates = env.actions_available_at(env.state)
        expected_next_states = {}
        for action in action_candidates:
            expected_next_states[action] = env.move(env.state, action, env.state.turn.value)

        observation = {
            'state': env.state,
            'action_candidates': action_candidates,
            'expected_next_states': expected_next_states
        }

        return observation

    def policy(self, observation):
        while True:
            action_str = input('打ちたい場所を入力してください：')
            for action in observation['action_candidates']:
                if action.name == action_str:
                    return action 
            print('入力に誤りがあります')

class RandomAgent():
    '''
    とれる行動からランダムに選択するエージェント
    '''
    def __init__(self, player_mark):
        self.player_mark = player_mark

    def observe(self, env):
        action_candidates = env.actions_available_at(env.state)
        expected_next_states = {}
        for action in action_candidates:
            expected_next_states[action] = env.move(env.state, action, env.state.turn.value)

        observation = {
            'state': env.state,
            'action_candidates': action_candidates,
            'expected_next_states': expected_next_states
        }

        return observation

    def policy(self, observation):
        policy_action = random.choice(observation['action_candidates'])
        return policy_action

class ValueIterationAgent():
    '''
    ValueIterationで得られた価値を用いて行動するエージェント
    '''
    def __init__(self, player_mark):
        self.player_mark = player_mark

        if self.player_mark == 1:
            with open('V_for_CIRCLE.pkl', 'rb') as f:
                self.V = pickle.load(f)
        elif self.player_mark == -1:
            with open('V_for_CROSS.pkl', 'rb') as f:
                self.V = pickle.load(f)

    def observe(self, env):
        action_candidates = env.actions_available_at(env.state)
        expected_next_states = {}
        for action in action_candidates:
            expected_next_states[action] = env.move(env.state, action, env.state.turn.value)

        observation = {
            'state': env.state,
            'action_candidates': action_candidates,
            'expected_next_states': expected_next_states
        }

        return observation

    def policy(self, observation):
        # 価値最大となる行動を1つ見つける
        max_V = -np.inf
        policy_action_candidate = None
        for action in observation['action_candidates']:
            expected_next_state = observation['expected_next_states'][action]
            if self.V[expected_next_state] > max_V:
                max_V = self.V[expected_next_state]
                policy_action_candidate = action
        
        # 価値最大となる行動が複数ある場合は全列挙してからランダムサンプリング
        policy_action_candidates = [policy_action_candidate]
        for action in observation['action_candidates']:
            expected_next_state = observation['expected_next_states'][action]
            if self.V[expected_next_state] == max_V:
                policy_action_candidates.append(action)        
        policy_action = random.choice(policy_action_candidates)

        return policy_action

def main(arg):
    # プレイヤーの先手後手の決定
    # ここでいう「プレイヤー」は報酬を最大化したい側を指す
    player_mark = arg # 〇（先手）: 1, ×（後手）: -1

    # 環境インスタンスの生成
    env = tic_tac_toe_environment.Environment(player_mark)

    # エージェントインスタンスの生成（プレイヤー，相手）
    player = ValueIterationAgent(player_mark)
    opponent = InputAgent(player_mark * -1)

    # ゲーム実施
    for _ in range(1):
        # 環境を初期化
        state = env.reset()
        total_reward = 0
        is_done = False
        print('------ 0手目 -----')
        print(state.gboard)
        print('')

        # 決着がつくまで行動
        while True:
            # 1.現在の状態で取りうる行動を取得
            # 2.戦略が行動を選択する
            # 3.行動により次の状態と報酬が決まる
            if player_mark == 1: # プレイヤーが先手番の場合
                # プレイヤーの行動
                observation = player.observe(env)
                action = player.policy(observation)
                next_state, reward, is_done = env.step(action, player_mark)
                total_reward += reward
                state = copy.deepcopy(next_state)
                print(f'------ {state.step}手目 -----')
                print(next_state.gboard)
                print('')
                if is_done:              
                    break

                # 相手の行動
                observation = opponent.observe(env)
                action = opponent.policy(observation)
                next_state, reward, is_done = env.step(action, player_mark*-1)
                total_reward += reward
                state = copy.deepcopy(next_state)
                print(f'------ {state.step}手目 -----')
                print(next_state.gboard)
                print('')
                if is_done:              
                    break

            else: # プレイヤーが後手番の場合
                # 相手の行動 
                observation = opponent.observe(env)
                action = opponent.policy(observation)
                next_state, reward, is_done = env.step(action, player_mark*-1)
                total_reward += reward
                state = copy.deepcopy(next_state)
                print(f'------ {state.step}手目 -----')
                print(next_state.gboard)
                print('')
                if is_done:              
                    break

                # 相手の行動
                observation = player.observe(env)
                action = player.policy(observation)
                next_state, reward, is_done = env.step(action, player_mark)
                total_reward += reward
                state = copy.deepcopy(next_state)
                print(f'------ {state.step}手目 -----')
                print(next_state.gboard)
                print('') 
                if is_done:              
                    break

        if state.status == tic_tac_toe_environment.Status.CIRCLE_WIN:
            print('〇（先手）の勝ち')
        elif state.status == tic_tac_toe_environment.Status.CROSS_WIN:
            print('×（後手）の勝ち')
        elif state.status == tic_tac_toe_environment.Status.DRAW:
            print('引き分け')

if __name__ == '__main__':
    main(int(sys.argv[1]))
