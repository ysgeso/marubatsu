# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
        
def test_judge(testcases, debug:bool=False):
    """ Marubastu クラスの judge メソッドのテスト
    
        Args:
            testcases:
                テストケースの dict
                dict のキーは、テストデータに対して judge メソッドを実行した際の、期待される返り値
                dict の値は、対応する、下記のデータ構造を持つテストデータ
                    * 着手するマスの座標を表す Excel 座標を "," で区切って連結した下記のような文字列
                        "A1,A2,A3"
                    * Excel 座標の順番は、着手を行う順番に対応する
                    * マスの座標は、"A1" のような文字列（Excel 座標）で表現する
            debug:
                True の場合、テストケースによって着手が行われたゲーム盤を表示する
    """
    
    print("Start")
    for winner, testdata_list in testcases.items():
        print("test winner =", winner) 
        for testdata in testdata_list:
            mb = Marubatsu()
            for coord in [] if testdata == "" else testdata.split(","):
                x, y = excel_to_xy(coord)            
                mb.move(x, y)
            if debug:
                print(mb)

            if mb.judge() == winner:
                print("o", end="")
            else:
                print()
                print("====================")
                print("test_judge error!")
                print(mb)
                print("mb.judge():", mb.judge())
                print("winner:    ", winner)
                print("====================")
        print()
    print("Finished")
            
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
