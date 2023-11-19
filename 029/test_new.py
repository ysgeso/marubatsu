# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu
        
# 1. x 座標と y 座標を直接並べる場合
        
def xytext_to_xy_1(coord):
    x, y = coord
    return int(x), int(y)

# 1.1 xy 文字座標を直接連結する場合
# 例："0001101120"

def text_to_list_1_1(coords):
    coord_list = [ coords[i:i+2] for i in range(0, len(coords), 2) ]
    return coord_list

def test_judge_1_1(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in text_to_list_1_1(testdata):
            x, y = xytext_to_xy_1(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")

# 1.2 xy 文字座標を "," で区切って連結する場合
# 例："00,01,10,11,20"

def test_judge_1_2(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata.split(","):
            x, y = xytext_to_xy_1(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 2. x 座標と y 座標を "," で区切って並べる場合

def xytext_to_xy_2(coord):
    x, y = coord.split(",")
    return int(x), int(y)

# 2.1 xy 文字座標を直接連結する場合
# 例："0,00,11,01,12,0"

def text_to_list_2_1(coords):
    coord_list = [ coords[i:i+3] for i in range(0, len(coords), 3) ]
    return coord_list

def test_judge_2_1(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in text_to_list_2_1(testdata):
            x, y = xytext_to_xy_2(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")

# 2.2 xy 文字座標を "," で区切って連結する場合
# 例："0,0,0,1,1,0,1,1,2,0"

def text_to_xylist(coords):
    coord_list = coords.split(",")
    xy_list = []
    for i in range(0, len(coord_list), 2):
        x, y = coord_list[i:i+2]
        xy_list.append([int(x), int(y)])
    return xy_list

def test_judge_2_2(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for x, y in text_to_xylist(testdata):
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")

# 2.3 xy 文字座標を ":" で区切って連結する場合
# 例："0,0:0,1:1,0:1,1:2,0"
       
def test_judge_2_3(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in testdata.split(":"):
            x, y = xytext_to_xy_2(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 3. x 座標と y 座標を数学と同じ文字列で記述する場合

def xytext_to_xy_3(coord):
    x, y = coord[1:-1].split(",")
    return int(x), int(y)

# 3.1 xy 文字座標を直接連結する場合
# 例："(0,0)(0,1)(1,0)(1,1)(2,0)"

def text_to_list_3_1(coords):
    coord_list = [ coords[i:i+5] for i in range(0, len(coords), 5) ]
    return coord_list

def test_judge(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in text_to_list_3_1(testdata):
            x, y = xytext_to_xy_3(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")

# 3.2 2 桁以上の場合の xy 文字座標を直接連結する場合
# 例："(10,10)(0,1)(1,0)(1,1)(2,0)"

def text_to_list_3_2(coords):
    coord_list = coords[1:-1].split(")(")
    return coord_list

def xytext_to_xy_3_2(coord):
    x, y = coord.split(",")
    return int(x), int(y)

def test_judge(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in text_to_list_3_2(testdata):
            x, y = xytext_to_xy_3_2(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")

# 3.3 xy 文字座標を ":" で区切って連結する場合
# 例："(0,0),(0,1),(1,0),(1,1),(2,0)"

# 3.3.1 split を使う場合

def text_to_list_3_3_1(coords):
    coord_list = coords[1:-1].split("),(")
    return coord_list

def test_judge(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in text_to_list_3_3_1(testdata):
            x, y = xytext_to_xy_3_2(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")
            
# 3.3.2 split を使わない場合

def text_to_list_3_3_2(coords):
    coord_list = [ coords[i:i+5] for i in range(0, len(coords), 6) ]
    return coord_list

def xytext_to_xy_3_3_2(coord):
    x, y = coord[1:-1].split(",")
    return int(x), int(y)


def test_judge(testcases):
    for testcase in testcases:
        testdata, winner = testcase
        mb = Marubatsu()
        for coord in text_to_list_3_3_2(testdata):
            x, y = xytext_to_xy_3_3_2(coord)            
            mb.move(x, y)
        print(mb)

        if mb.judge() == winner:
            print("ok")
        else:
            print("error!")