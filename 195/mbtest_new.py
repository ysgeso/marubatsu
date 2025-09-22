# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
        
def test_judge(testcases=None, debug:bool=False, mbparams:dict={}):
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
                    
                省略した場合は、MC/DC と簡易的な経路網羅のテストケースでテストが行われる
            debug:
                True の場合、テストケースによって着手が行われたゲーム盤を表示する
            mbparams:
                Marubatsu クラスのインスタンスを作成する際に実引数に記述する値を表す dict
    """
    
    if testcases is None:
        testcases = {
            # 決着がついていない場合のテストケース
            Marubatsu.PLAYING: [
                # ゲーム盤に一つもマークが配置されていない場合のテストケース
                "",
                # 一つだけマークが配置されていない場合のテストケース
                "C3,A2,B1,B2,C2,C1,A3,B3",
                "A1,A2,C3,B2,C2,C1,A3,B3",
                "A1,A2,B1,B2,C2,C3,A3,B3",
                "A1,C3,B1,B2,C2,C1,A3,B3",
                "A1,A2,B1,C3,C2,C1,A3,B3",
                "A1,A2,B1,B2,C3,C1,A3,B3",
                "A1,A2,B1,B2,C2,C1,C3,B3",
                "A1,A2,B1,B2,A3,C1,C2,C3",
                "A1,A2,B1,B2,C2,C1,A3,B3",
            ],   
            # 〇の勝利のテストケース
            Marubatsu.CIRCLE: [
                "A1,A2,B1,B2,C1",
                "A2,A1,B2,B1,C2",
                "A3,A1,B3,B1,C3",
                "A1,B1,A2,B2,A3",
                "B1,A1,B2,A2,B3",
                "C1,A1,C2,A2,C3",
                "A1,A2,B2,A3,C3",
                "A3,A1,B2,A2,C1",
                # 簡易的な組み合わせ網羅の 6 のテストケース
                "A1,B1,A2,B2,B3,C1,C3,C2,A3", 
            ],
            # × の勝利のテストケース
            Marubatsu.CROSS: [
                "A2,A1,B2,B1,A3,C1",
                "A1,A2,B1,B2,A3,C2",
                "A1,A3,B1,B3,A2,C3",
                "B1,A1,B2,A2,C1,A3",
                "A1,B1,A2,B2,C1,B3",
                "A1,C1,A2,C2,B1,C3",
                "A2,A1,A3,B2,B1,C3",
                "A1,C1,B1,B2,A2,A3",
            ],
            # 引き分けの場合のテストケース
            Marubatsu.DRAW: [
                "A1,A2,B1,B2,C2,C1,A3,B3,C3",
            ], 
        }
            
    print("Start")
    for winner, testdata_list in testcases.items():
        print("test winner =", winner) 
        for testdata in testdata_list:
            mb = Marubatsu(**mbparams)
            for coord in [] if testdata == "" else testdata.split(","):
                x, y = excel_to_xy(coord)    
                move = mb.board.xy_to_move(x, y)           
                mb.move(move)
            if debug:
                print(mb)

            if mb.judge() == winner:
                if debug:
                    print("ok")
                else:
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
