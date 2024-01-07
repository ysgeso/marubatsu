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

    print(f"{ai[0].__name__} VS {ai[1].__name__}")
    
    mb = Marubatsu()

    # ai[0] VS ai[1] と ai[1] VS a[0] の対戦を match_num 回行い、通算成績を数える
    count_list = [ defaultdict(int), defaultdict(int)]
    for _ in range(match_num):
        count_list[0][mb.play(ai, verbose=False)] += 1
        count_list[1][mb.play(ai=[ai[1], ai[0]], verbose=False)] += 1

    # ai[0] から見た通算成績を計算する
    count_list_ai0 = [
        # ai[0] VS ai[1] の場合の、ai[0] から見た通算成績
        { 
            "win": count_list[0][Marubatsu.CIRCLE],
            "lose": count_list[0][Marubatsu.CROSS],
            "draw": count_list[0][Marubatsu.DRAW],
        },
        # ai[1] VS ai[0] の場合の、ai[0] から見た通算成績
        { 
            "win": count_list[1][Marubatsu.CROSS],
            "lose": count_list[1][Marubatsu.CIRCLE],
            "draw": count_list[1][Marubatsu.DRAW],
        },
    ]           

    # 両方の対戦の通算成績の合計を計算する
    count_list_ai0.append({})
    for key in count_list_ai0[0]:
        count_list_ai0[2][key] = count_list_ai0[0][key] + count_list_ai0[1][key]

    # それぞれの比率を計算し、ratio_list に代入する
    ratio_list = [ {}, {}, {} ]
    for i in range(3):
        for key in count_list_ai0[i]:
            ratio_list[i][key] = count_list_ai0[i][key] / sum(count_list_ai0[i].values())
            
    # 各行の先頭に表示する文字列のリスト
    item_text_list = [ Marubatsu.CIRCLE, Marubatsu.CROSS, "total" ]    
    
    # 通算成績の回数と比率の表示
    width = max(len(str(match_num * 2)), 7)
    diff_list = [ ("count", count_list_ai0, f"{width}d"),
                  ("ratio", ratio_list, f"{width}.1%") ]
    for title, data, format in diff_list:
        print(title, end="")
        for key in data[0]:
            print(f" {key:>{width}}", end="")
        print()
        for i in range(3):
            print(f"{item_text_list[i]:5}", end="")
            for value in data[i].values():
                print(f" {value:{format}}", end="")
            print()
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