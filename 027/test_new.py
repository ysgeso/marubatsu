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
            

# 以下、その 27 で紹介したさまざまな excel_to_xy の定義
# なお、docstring は、上記の excel_to_xy と同じなので省略する

def excel_to_xy_1(coord):
    if coord == "A1":
        return 0, 0
    elif coord == "A2":
        return 0, 1
    elif coord == "A3":
        return 0, 2
    elif coord == "B1":
        return 1, 0
    elif coord == "B2":
        return 1, 1
    elif coord == "B3":
        return 1, 2
    elif coord == "C1":
        return 2, 0
    elif coord == "C2":
        return 2, 1
    elif coord == "C3":
        return 2, 2
    else:
        print("invalid coord", coord)

def excel_to_xy_2(coord):
    excel_to_xy_table = {
        "A1": [0, 0],
        "A2": [0, 1],
        "A3": [0, 2],
        "B1": [1, 0],
        "B2": [1, 1],
        "B3": [1, 2],
        "C1": [2, 0],
        "C2": [2, 1],
        "C3": [2, 2],
    }
    return excel_to_xy_table[coord]

def excel_to_xy_3(coord):
    excel_to_x_table = {
        "A": 0,
        "B": 1,
        "C": 2,
    }
    excel_to_y_table = {
        "1": 0,
        "2": 1,
        "3": 2,
    }

    x, y = coord
    return excel_to_x_table[x], excel_to_y_table[y]

def excel_to_xy_4(coord):
    excel_to_x_table = {
        "A": 0,
        "B": 1,
        "C": 2,
    }
    x, y = coord
    return excel_to_x_table[x], int(y) - 1

def excel_to_xy_4_reg(coord):
    excel_to_x_table = {
        "A": 0,
        "B": 1,
        "C": 2,
    }

    # 正規表現を使って、Excel 座標のアルファベットの部分と整数の部分を分離する
    m = re.fullmatch("([A-Z]+)(\d+)", coord)
    # 分離したデータを x と y に代入する
    x = m.group(1)
    y = m.group(2)
    return excel_to_x_table[x], int(y) - 1

def excel_to_xy_6(coord):
    x, y = coord
    return ord(x) - 65, int(y) - 1