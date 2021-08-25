from enum import Enum
import numpy as np
import copy
import itertools

class State():
    '''
    2次元グリッドによる盤面（状態）の定義：
    self.board（盤面）
        0: 印が書かれていないマス
        1: 〇（先手）が書かれているマス
        -1: ×（後手）が書かれているマス
    self.turn（手番）
        Turn.CIRCLE：先手
        Turn.CROSS：後手
    self.step（手数）
    self.status（ステータス）
        Status.UNDECIDED : 未決着
        Status.CIRCLE_WIN : 先手の勝利
        Status.CROSS_WIN : 後手の勝利
        Status.DRAW : 引き分け
        Status.INFEASIBLE : 存在しえない盤面
    '''
    def __init__(self, board=np.zeros((3,3))):
        '''
        コンストラクタ。引数がない場合は初期盤面を生成
        '''
        self.board = board
        self.gboard = self.__board_to_gboard(self.board)
        self.turn = self.__check_turn(self.board)
        self.step = self.__check_step(self.board)
        self.status = self.__check_status(self.board, self.step)

    def __board_to_gboard(self, board):
        '''
        ○×表示の盤面を返す
        '''
        gboard_tmp = board.astype(int).astype(str)
        gboard_tmp2 = np.where(gboard_tmp == '1', '〇', gboard_tmp)
        gboard_tmp3 = np.where(gboard_tmp2 == '-1', '×', gboard_tmp2)
        gboard = np.where(gboard_tmp3 == '0', '―', gboard_tmp3)
        return gboard

    def __check_turn(self, board):
        '''
        手番を返す
        '''
        total = np.sum(board)

        # 盤面の総和が1なら後手番，0なら先手番
        return Turn.CROSS if total else Turn.CIRCLE

    def __check_step(self, board):
        '''
        （この盤面までの）手数を返す
        '''
        # 9-（盤面の0の数）が手数
        step = 9
        for row in board:
            for cell in row:
                if cell == 0:
                    step -= 1

        return step

    def __check_status(self, board, step):
        '''
        状態が「未決着，先手勝利，後手勝利，存在しえない盤面」
        のいずれであるかを返す
        '''
        circle_line = 0 # 〇が揃っているラインの数
        cross_line = 0 # ×が揃っているラインの数

        # 行のチェック
        for row_sum in np.sum(board, axis=0):
            if row_sum == 3:
                circle_line += 1
            elif row_sum == -3:
                cross_line += 1

        # 列のチェック
        for column_sum in np.sum(board, axis=1):
            if column_sum == 3:
                circle_line += 1
            elif column_sum == -3:
                cross_line += 1

        # 斜めのチェック
        back_slash_sum = board[0,0] + board[1,1] + board[2,2]
        if back_slash_sum == 3:
            circle_line += 1
        elif back_slash_sum == -3:
            cross_line += 1

        slash_sum = board[2,0] + board[1,1] + board[0,2]
        if slash_sum == 3:
            circle_line += 1
        elif slash_sum == -3:
            cross_line += 1

        # 先手と後手の手数は同じか，先手が1回多いかのどちらかしかない
        if np.sum(board) < 0 or np.sum(board) > 1:
            status = Status.INFEASIBLE     
        # 両方の線ができることはない
        elif circle_line and cross_line:
            status = Status.INFEASIBLE
        # 最終手以外で2ラインできることはない
        elif (step < 9 and circle_line == 2) or (step < 9 and cross_line == 2):
            status = Status.INFEASIBLE
        # 上記を除けば，ラインの有無で勝敗が判定可能
        elif circle_line:
            status = Status.CIRCLE_WIN
        elif cross_line:
            status = Status.CROSS_WIN
        # どちらのラインも出来ていない場合は引き分けか未決着
        elif step == 9:
            status = Status.DRAW
        else:
            status = Status.UNDECIDED

        return status

    def reset(self):
        '''
        リセットする
        '''
        self.board = np.zeros((3,3))
        self.turn = self.__check_turn(self.board)
        self.step = self.__check_step(self.board)
        self.status = self.__check_status(self.board, self.step)
        return self

    def __repr__(self):
        return "<State: {}>".format(self.board.flatten())

    # 辞書のキーとして使うために必要
    def __hash__(self):
        return hash(tuple(self.board.flatten()))

    # 辞書のキーとして使うために必要
    def __eq__(self, other):
        return (self.board == other.board).all()

class Turn(Enum):
    '''
    手番の定義（列挙型）
    '''
    CIRCLE = 1 # 〇（先手）
    CROSS = -1 # ×（後手）

class Status(Enum):
    '''
    ステータスの定義（列挙型）
    '''
    UNDECIDED = 0 # 勝敗未確定
    CIRCLE_WIN = 1 # 先手勝利
    CROSS_WIN = -1 # 後手勝利
    DRAW = 8 # 引き分け
    INFEASIBLE = 9 # 存在しえない盤面

class Actions(Enum):
    '''
    行動の定義（列挙型）。該当のマス目に印を書く
    '''
    TL = (0, 0) # TopLeft
    TC = (0, 1) # TopCenter
    TR = (0, 2) # TopRight
    CL = (1, 0) # CenterLeft
    C = (1, 1) # Center
    CR = (1, 2) # CenterRight
    BL = (2, 0) # BottomLeft
    BC = (2, 1) # BottomCenter
    BR = (2, 2) # BottomRight


class Environment():
    '''
    環境の定義
    '''
    def __init__(self, player_mark):
        '''
        コンストラクタ。
        報酬の与え方が変わるためプレイヤー（報酬を最大化したい側）
        の手番を引数として与える
        '''
        # プレイヤー側のマーク
        self.player_mark = player_mark
        # 盤面の初期化
        self.state = State()

    @property
    def actions(self):
        '''
        全ての行動一覧
        '''
        return list(Actions)

    @property
    def states(self):
        '''
        取りうる状態一覧
        '''
        states = []

        # 3^9通り総当たり
        i = [-1, 0, 1]
        for i00, i01, i02, i10, i11, i12, i20, i21, i22 \
            in itertools.product(i, i, i, i, i, i, i, i, i):
            
            board = np.array(
                        [[i00, i01, i02],
                         [i10, i11, i12],
                         [i20, i21, i22]]
                    )
            state = State(board)

            # あり得る状態のみストック
            if state.status != Status.INFEASIBLE:
                states.append(state)

        return states

    def actions_available_at(self, state):
        '''
        状態stateにおいて取れる行動一覧を返す関数
        '''
        actions = []
        # 勝負が未決着の場合は，boardが0になっているところに印を書ける
        if state.status == Status.UNDECIDED:
            for action in Actions:
                if state.board[action.value] == 0:
                    actions.append(action)

        return actions

    def move(self, state, action, mark):
        '''
        状態stateにおいて行動actionをとる
        '''
        # 行動をとる
        next_board = copy.deepcopy(state.board)
        next_board[action.value] = mark

        # 次の状態インスタンスを生成
        next_state = State(next_board)

        return next_state

    def reward_func(self, state):
        '''
        状態stateの報酬
        '''
        # 勝っていれば報酬を与える
        if state.status.value == self.player_mark:
            reward = 1
            is_done = True
        # 負けていれば負の報酬を与える 
        elif state.status.value == self.player_mark * -1:
            reward = -1
            is_done = True
        # 引き分け時は報酬0
        elif state.status == Status.DRAW:
            reward = 0
            is_done = True
        # 未確定時は報酬0
        elif state.status == Status.UNDECIDED:
            reward = 0
            is_done = False
        # INFEASIBLEはおかしい
        else:
            print('おかしい')

        return reward, is_done

    def transit_func(self, state, action, mark):
        '''
        状態stateにおける行動actionによる遷移確率
        ここでは確率1で意図した行動を取れるとする
        '''
        transition_probs = {}
        next_state = self.move(state, action, mark)
        transition_probs[next_state] = 1

        return transition_probs

    def transit(self, state, action, mark):
        '''
        遷移
        '''
        transition_probs = self.transit_func(state, action, mark)

        next_states = []
        probs = []
        for s in transition_probs:
            next_states.append(s)
            probs.append(transition_probs[s])

        next_state = np.random.choice(next_states, p=probs)
        reward, is_done = self.reward_func(next_state)
        return next_state, reward, is_done

    def step(self, action, mark):
        '''
        ステップを進める
        '''
        next_state, reward, is_done = self.transit(self.state, action, mark)
        self.state = copy.deepcopy(next_state)

        return next_state, reward, is_done

    def reset(self):
        '''
        環境のリセット
        '''
        self.state = self.state.reset()
        return self.state