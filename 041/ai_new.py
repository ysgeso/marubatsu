# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
from random import choice
from collections import defaultdict

def ai_match(ai:list, match_num:int=10000):
    """AIどうしの対戦を行い、通算成績を表示する

    Args:
        ai:
            それぞれの手番を担当する AI の関数指定する list
            0 番の要素が 〇 の手番、1 番の要素が × の手番を表す
            AI の処理を行う関数の仮引数は Marubatsu クラスのインスタンスで、
            着手を行う座標を表す (x, y) の形式の tuple を返すものとする
        match_num:
            対戦を行う回数
    """

    mb = Marubatsu()

    # ai[0] VS ai[1] の対戦を match_num 回行い、通算成績を数える
    count = defaultdict(int)
    for _ in range(match_num):
        count[mb.play(ai, verbose=False)] += 1

    # それぞれの比率を計算し、ratio に代入する
    ratio = {}
    for key in count.keys():
        ratio[key] = count[key] / match_num

    # 〇の勝利、×の勝利、引き分けの順番で表示することを表す list 
    order_list = [Marubatsu.CIRCLE, Marubatsu.CROSS, Marubatsu.DRAW]

    # 通算成績の回数と比率の表示
    diff_list = [ ("count", count, "d"), ("ratio", ratio, ".1%") ]
    for title, data, format in diff_list:
        print(title, end="")
        for key in order_list:
            print(f" {key} {data[key]:{format}}", end="")
        print()
    

def ai1(mb:Marubatsu) -> tuple[int, int]:
    """左上から順に空いているマスを探し、最初に見つかったマスに着手する AI.

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス

    Returns:
        着手する座標を表す tuple
    """

    for y in range(mb.BOARD_SIZE):
        for x in range(mb.BOARD_SIZE):
            if mb.board[x][y] == Marubatsu.EMPTY:
                return x, y

def ai2(mb:Marubatsu) -> tuple[int, int]:
    """ランダムなマスに着手する AI.

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス

    Returns:
        着手する座標を表す tuple
    """
    legal_moves = mb.calc_legal_moves()
    return choice(legal_moves)