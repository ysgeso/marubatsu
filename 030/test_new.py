# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
        
# 数値座標を list で記述した場合

# if 文で num_to_xy を定義した場合
def num_to_xy_1_1(coord):
    if coord == 0:
        return 0, 0
    elif coord == 1:
        return 1, 0
    elif coord == 2:
        return 2, 0
    elif coord == 3:
        return 0, 1
    elif coord == 4:
        return 1, 1
    elif coord == 5:
        return 2, 1
    elif coord == 6:
        return 0, 2
    elif coord == 7:
        return 1, 2
    elif coord == 8:
        return 2, 2
    else:
        print("invalid coord", coord)
               
def test_judge_1_1(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata:
            x, y = num_to_xy_1_1(coord)
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# テーブルで num_to_xy を定義した場合
def num_to_xy_1_2(coord):
    num_to_xy_table = [
        [0, 0], [1, 0], [2, 0],
        [0, 1], [1, 1], [2, 1],
        [0, 2], [1, 2], [2, 2],
    ]
    return num_to_xy_table[coord]
        
def test_judge_1_2(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata:
            x, y = num_to_xy_1_2(coord)
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 計算で num_to_xy を定義した場合
def num_to_xy_1_3(coord):
    x = coord % 3
    y = coord // 3
    return x, y

def test_judge_1_3(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata:
            x, y = num_to_xy_1_3(coord)
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 数値座標を直接連結した場合
def num_to_xy_2(coord):
    coord = int(coord)
    x = coord % 3
    y = coord // 3
    return x, y

def test_judge_2(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata:
            x, y = num_to_xy_2(coord)
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 数値座標を "," で区切って連結した場合
def test_judge_3(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata.split(","):
            x, y = num_to_xy_2(coord)
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 着手順の文字列の場合
def test_judge_4(testcases):
    for testcase in testcases:
        move_order, winner = testcase
        mb = Marubatsu()
        for i in range(1, 10):
            if str(i) not in move_order:
                break
            coord = move_order.index(str(i))
            x, y = num_to_xy_2(coord)
            mb.move(x, y)
        print(mb)
 
        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 着手順を "," で区切って連結した場合
def test_judge_5(testcases):
    for testcase in testcases:
        move_order, winner = testcase
        move_order = move_order.split(",")
        mb = Marubatsu()
        for i in range(1, 10):
            if str(i) not in move_order:
                break
            coord = move_order.index(str(i))
            x, y = num_to_xy_2(coord)
            mb.move(x, y)
        print(mb)
 
        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")

# 着手順を list で記述した場合
def test_judge_6(testcases):
    for testcase in testcases:
        move_order, winner = testcase
        mb = Marubatsu()
        for i in range(1, 10):
            if i not in move_order:
                break
            coord = move_order.index(i)
            x, y = num_to_xy_2(coord)
            mb.move(x, y)
        print(mb)
 
        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")