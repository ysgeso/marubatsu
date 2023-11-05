# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu

def test_judge(testcase: list[list[int]]):
    """ Marubastu クラスの judge メソッドのテスト
    
        Args:
            testcase:
                テストケースを表すデータで、以下のようなデータ構造を持つ
                    * 着手するマスの座標を表すデータを要素とする list で表現する
                    * list の要素の順番は、着手を行う順番に対応する
                    * マスの座標は、マスの x 座標と y 座標を要素とする list で表現する
    """
    mb = Marubatsu()
    for x, y in testcase:
        mb.move(x, y)
    print(mb)

    if mb.judge() == Marubatsu.CIRCLE:
        print("ok")
    else:
        print("error!")