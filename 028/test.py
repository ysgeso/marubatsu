# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
import re
        
def test_judge(testcases):
    """ Marubastu クラスの judge メソッドのテスト
    
        Args:
            testcases:
                テストケースの list
                下記は、list 内の各テストケース を testcase と表記した場合のデータ構造
                    testcase[0]:                     
                        * 着手するマスの座標を表すデータを要素とする list で表現する
                        * list の要素の順番は、着手を行う順番に対応する
                        * マスの座標は、"A1" のような文字列（Excel 座標）で表現する
                    testcase[1]:
                        期待される judge メソッドの返り値
    """
    
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata:
            x, y = excel_to_xy(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
def excel_to_xy(coord: str) -> tuple(int):
    """ Excel 座標を xy 座標に変換する.
    
    "A1" のような、文字列で表現される Excel 座標を、
    (x, y) のような tuple で表現される xy 座標に変換した値を返す

    Args:
        coord:
            "A1" のような、文字列で表現されるExcel 座標
            ただし、x 座標は、"A"、"B"、"C" のいずれかのみとする      
        
    Returns:
        x 座標と y 座標を要素として持つ tuple
    """
    x, y = coord
    return "ABC".index(x), int(y) - 1            
            