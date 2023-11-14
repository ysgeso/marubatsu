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
                        * 着手するマスの座標を表す Excel 座標を "," で区切って連結した下記のような文字列
                          "A1,A2,A3"
                        * Excel 座標の順番は、着手を行う順番に対応する
                        * マスの座標は、"A1" のような文字列（Excel 座標）で表現する
                    testcase[1]:
                        期待される judge メソッドの返り値
    """
    
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata.split(","):
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


# 以下、その 28 で紹介したが採用しなかったさまざまな 関数の定義
# なお、docstring は省略する

def excels_to_list(excels):
    excel_list = []
    # excels の先頭から 2 文字ずつ文字を取り出す繰り返し処理
    for i in range(0, len(excels), 2):
        # i 文字目と、i + 1 文字目を連結した 2 文字を取り出す
        excel = excels[i] + excels[i + 1]
        excel_list.append(excel)
    return excel_list

def excels_to_list_2(excels):
    excel_list = []
    # excels の先頭から 2 文字ずつ文字を取り出す繰り返し処理
    for i in range(0, len(excels), 2):
        # i 文字目から 2 文字分を取り出す
        excel = excels[i:i+2]
        excel_list.append(excel)
    return excel_list

def excels_to_list_3(excels):
    excel_list = [ excels[i:i+2] for i in range(0, len(excels), 2) ]
    return excel_list

# Excel 座標を間を区切らずに連結したデータ構造に対する test_judge
def test_judge_1(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in excels_to_list(testdata):
            x, y = excel_to_xy(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")