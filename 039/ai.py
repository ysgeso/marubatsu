# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
from random import choice

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