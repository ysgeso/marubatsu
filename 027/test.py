# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
        
def test_judge(testcases):
    """ Marubastu クラスの judge メソッドのテスト
    
        Args:
            testcases:
                テストケースの list
                下記は、list 内の各テストケース を testcase と表記した場合のデータ構造
                    testcase[0]:                     
                        * 着手するマスの座標を表すデータを要素とする list で表現する
                        * list の要素の順番は、着手を行う順番に対応する
                        * マスの座標は、マスの x 座標と y 座標を要素とする list で表現する
                    testcase[1]:
                        期待される judge メソッドの返り値
    """
    
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for x, y in testdata:
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")