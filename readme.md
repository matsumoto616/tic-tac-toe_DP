### 動的計画法による○×ゲームの学習
- 価値反復法（Value Iteration）
- 戦略反復法（Policy Iteration）

### 使い方
#### ライブラリ
- numpyだけあればいいはず

#### 学習（Bellman方程式の反復計算による状態価値，戦略の決定）
planner.pyを実行。Value Iterationにより，先手番用の価値関数(V_for_CIRCLE.pkl)と後手番用の価値関数(V_for_CROSS.pkl)が出力される。
その後，Ploicy Iterationにより，先手番用の戦略(policy_for_CIRCLE.pkl)と後手番用の戦略(policy_for_CROSS.pkl)が出力される。
```
python planner.py
```

#### プレイ
学習済みの価値(V_for_CIRCLE.pkl，V_for_CROSS.pkl)や戦略（policy_for_CIRCLE.pkl，policy_for_CROSS.pkl）を用いて，対戦が可能。
```
python environment_demo.py agent1 agent2
```
agent1, agent2はそれぞれ先手番，後手番に対応し，下記から選択する。
- input : 標準入力から入力された手を選択するエージェント
- random : ランダムに手を選択するエージェント
- value : Value Iterationで得られた価値をもとに手を選択するエージェント
- policy : Policy Iterationで得られた価値をもとに手を選択するエージェント

**ただしagent1, agent2ともにvalueないしpolicyを選ぶことはできない（issue #2）**

inputエージェントを選択している場合，入力を求められたら，印をつけたい位置を入力する：

入力フォーマットは下記の通り：
- TL：TopLeft 左上
- TC：TopCenter 上
- TR：TopRight 右上
- CL：CenterLeft 左
- C：Center 真ん中
- CR：CenterRight 右
- BL：BottomLeft 左下
- BC：BottomCenter 下
- BR：BottomRight 右下

### 参考
コードの構成などは下記書籍を参考にした：
**「Pythonで学ぶ強化学習 ［改訂第２版］ 入門から実践まで」**
https://www.amazon.co.jp/dp/B082HNNGQG/ref=dp-kindle-redirect?_encoding=UTF8&btkr=1

### 序盤中盤終盤，隙がないと思うよ。

### Test 
