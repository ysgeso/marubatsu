# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from collections import defaultdict
from typing import NamedTuple
import random
import matplotlib as mlp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import japanize_matplotlib
import math
import ipywidgets as widgets
from tkinter import Tk, filedialog
import pickle
from datetime import datetime
import os
from gui import GUI
from copy import deepcopy
from gui import GUI

class Markpat(NamedTuple):   
    """マークのパターン.
    
    Attributes:
        last_turn (int):
            直前のターンのマークの数
        turn (int):
            現在のターンのマークの数
        empty (int):
            空のマスの数
    """
    
    last_turn: int
    turn: int
    empty: int

class Marubatsu:
    """ 〇×ゲーム.

    Attributes:
        クラス属性
        EMPTY (str):
            空のマスを表す文字列
        CIRCLE (str):
            〇 のマークを表す文字列
        CROSS (str):
            × のマークを表す文字列
        DRAW (str):
            引き分けを表す文字列
        PLAYING (str):
            決着がついていないことを表す文字列
        
        インスタンス属性
        BOARD_SIZE (int):
            ゲーム盤の縦横のサイズを表す数値
        board (list[list[str]):
            ゲーム盤を表す 2 次元配列の list
            2 つのインデックスは、順に x 座標、y 座標を表す
            空白のマスは " "、〇 のマスは "o"、× のマスは "x" を代入する
        move_count (int):
            着手を行った回数
        status (str):
            ゲームの状態
            CIRCLE、CROSS、DRAW、PLAYING のいずれかの状態が代入される
        last_move (tuple(int, int)):
            直前の着手の座標
        last_turn (str):
            直前の手番
        records: (list[tuple[int, int]])
            ゲームの棋譜
        board_records: (list[list[list[str]])
            各手数のゲーム盤のデータ
    """

    EMPTY = "."
    CIRCLE = "o"
    CROSS = "x"
    DRAW = "draw"
    PLAYING = "playing"
    
    def __init__(self, board_size: int=3, count_linemark:bool=False):
        """ イニシャライザ 
        
        Args:
            board_size:
                ゲーム盤の縦横のサイズ。デフォルト値は 3
            count_linemark:
                各直線上のマークの数を数えるかどうか。デフォルト値は False
        """

        # ゲーム盤の縦横のサイズ
        self.BOARD_SIZE = board_size
        # 各直線上のマークの数を数えるかどうか
        self.count_linemark = count_linemark
        # 〇×ゲーム盤を再起動するメソッドを呼び出す
        self.restart()

    def initialize_board(self):
        """ ゲーム盤のデータの初期化. """

        self.board = [[Marubatsu.EMPTY] * self.BOARD_SIZE for y in range(self.BOARD_SIZE)]

    def place_mark(self, x: int, y: int, mark: str) -> bool:
        """ ゲーム盤の指定したマスに指定したマークを配置する.

        (x, y) のマスに mark で指定したマークを配置する.
        (x, y) のマスがゲーム盤の範囲外の場合は、メッセージを表示する.
        (x, y) のマスに既にマークが配置済の場合は、メッセージを表示する.
        返り値として配置できたかどうかを表す論理型のデータを返す.

        Args:
            x:
                マークを配置するマスの x 座標
            y:
                マークを配置するマスの y 座標
            mark:
                配置するマークを表す文字列
                
        Returns:
            マークを配置できた場合は True、配置できなかった場合は False
        """

        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            if self.board[x][y] == Marubatsu.EMPTY:
                self.board[x][y] = mark
                return True
            else:
                print("(", x, ",", y, ") のマスにはマークが配置済です")
                return False
        else:
            print("(", x, ",", y, ") はゲーム盤の範囲外の座標です")
            return False   
        
    def remove_mark(self, x:int, y:int) -> bool:
        """ ゲーム盤の指定したマスに指定したマークを削除する.

        (x, y) のマスのマークを削除する.
        (x, y) のマスがゲーム盤の範囲外の場合は、メッセージを表示する.
        (x, y) のマスにマークが配置されていない場合は、メッセージを表示する.
        返り値として削除できたかどうかを表す論理型のデータを返す.

        Args:
            x:
                マークを削除するマスの x 座標
            y:
                マークを削除するマスの y 座標
                
        Returns:
            マークを削除できた場合は True、削除できなかった場合は False
        """
                
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            if self.board[x][y] != Marubatsu.EMPTY:
                self.board[x][y] = Marubatsu.EMPTY
                return True
            else:
                print("(", x, ",", y, ") のマスにはマークがありません")
                return False
        else:
            print("(", x, ",", y, ") はゲーム盤の範囲外の座標です")
            return False           
            
    def restart(self):
        """ 〇×ゲームを再起動する. """

        self.initialize_board()
        self.turn = Marubatsu.CIRCLE     
        self.move_count = 0
        self.status = Marubatsu.PLAYING
        self.last_move = -1, -1          
        self.last_turn = None
        self.records = [self.last_move]
        if self.count_linemark:
            self.rowcount = {
                Marubatsu.CIRCLE: [0] * self.BOARD_SIZE,
                Marubatsu.CROSS: [0] * self.BOARD_SIZE,
            }
            self.colcount = {
                Marubatsu.CIRCLE: [0] * self.BOARD_SIZE,
                Marubatsu.CROSS: [0] * self.BOARD_SIZE,
            }
            self.diacount = {
                Marubatsu.CIRCLE: [0] * 2,
                Marubatsu.CROSS: [0] * 2,
            }
    
    def move(self, x: int, y: int):
        """ ゲーム盤の指定したマスに着手する.

        Args:
            x:
                マークを配置するマスの x 座標
            y:
                マークを配置するマスの y 座標
        """

        if self.place_mark(x, y, self.turn):
            self.last_turn = self.turn
            self.turn = Marubatsu.CROSS if self.turn == Marubatsu.CIRCLE else Marubatsu.CIRCLE  
            self.move_count += 1
            self.last_move = x, y
            if self.count_linemark:
                self.colcount[self.last_turn][x] += 1
                self.rowcount[self.last_turn][y] += 1
                if x == y:
                    self.diacount[self.last_turn][0] += 1        
                if x + y == self.BOARD_SIZE - 1:
                    self.diacount[self.last_turn][1] += 1        
            self.status = self.judge()
            if len(self.records) <= self.move_count:            
                self.records.append(self.last_move)
            else:
                self.records[self.move_count] = self.last_move
                self.records = self.records[0:self.move_count + 1]
                    
    def unmove(self):
        """ 直前の着手を取り消す.
        
        ゲーム開始時の局面の場合は何も行わない
        """
                
        if self.move_count > 0:
            x, y = self.last_move
            if self.count_linemark:
                self.colcount[self.last_turn][x] -= 1
                self.rowcount[self.last_turn][y] -= 1
                if x == y:
                    self.diacount[self.last_turn][0] -= 1        
                if x + y == self.BOARD_SIZE - 1:
                    self.diacount[self.last_turn][1] -= 1           
            if self.move_count == 0:
                self.last_move = (-1, -1)
            self.move_count -= 1
            self.turn, self.last_turn = self.last_turn, self.turn
            self.status = Marubatsu.PLAYING
            x, y = self.records.pop()
            self.remove_mark(x, y)
            
            self.last_move = self.records[-1]                 
                            
    def change_step(self, step:int):
        """step 手目の局面に移動する.
        
        Args:
            step:
                移動する局面の手数
        """
        # step の範囲を正しい範囲に修正する
        step = max(0, min(len(self.records) - 1, step))
        records = self.records
        self.restart()
        for x, y in records[1:step+1]:
            self.move(x, y)
        self.records = records

    def judge(self) -> str:
        """ 勝敗判定.
        
        Returns:
            以下のいずれかの値を返す
            Marubatsu.CIRCLE:  〇 の勝利
            Marubatsu.CROSS:   × の勝利
            Marubatsu.DRAW:    引き分け
            Marubatsu.PLAYING: 決着がついていない
        """
        
        if self.move_count < self.BOARD_SIZE * 2 - 1:
            return Marubatsu.PLAYING
        # 直前に着手を行ったプレイヤーの勝利の判定
        if self.is_winner(self.last_turn):
            return self.last_turn
        # 引き分けの判定
        elif self.is_full():
            return Marubatsu.DRAW
        # 上記のどれでもなければ決着がついていない
        else:
            return Marubatsu.PLAYING          
            
    def __str__(self):
        # ゲームの決着がついていない場合は、手番を表示する
        if self.status == Marubatsu.PLAYING:
            text = "Turn " + self.turn + "\n"
        # 決着がついていれば勝者を表示する
        else:
            text = "winner " + self.status + "\n"
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                lastx, lasty = self.last_move
                if x == lastx and y == lasty:
                    text += self.board[x][y].upper()
                else:
                    text += self.board[x][y]
            text += "\n"
        return text
    
    def board_to_str(self) -> str:
        """board 属性の要素を連結した文字列を計算して返す
        
        Returns:
            board 属性の要素を連結した文字列
        """

        txt = ""
        for col in self.board:
            txt += "".join(col)
        return txt
    
    def is_winner(self, player:str) -> bool:
        """player のプレイヤーの勝利判定.

        Args:
            player: 
                判定するプレイヤーを表す文字列
                Marubatsu.CIRCLE または Marubatsu.CROSS を指定する

        Returns:
            player のプレイヤーが勝利している場合は True
            そうでない場合は False
        """
        
        x, y = self.last_move
        if self.count_linemark:
            if self.rowcount[player][y] == self.BOARD_SIZE or \
            self.colcount[player][x] == self.BOARD_SIZE:
                return True
            # 左上から右下方向の判定
            if x == y and self.diacount[player][0] == self.BOARD_SIZE:
                return True
            # 右上から左下方向の判定
            if x + y == self.BOARD_SIZE - 1 and \
                self.diacount[player][1] == self.BOARD_SIZE:
                return True
        else:
            if self.is_same(player, coord=[0, y], dx=1, dy=0) or \
            self.is_same(player, coord=[x, 0], dx=0, dy=1):
                return True
            # 左上から右下方向の判定
            if x == y and self.is_same(player, coord=[0, 0], dx=1, dy=1):
                return True
            # 右上から左下方向の判定
            if x + y == self.BOARD_SIZE - 1 and \
                self.is_same(player, coord=[self.BOARD_SIZE - 1, 0], dx=-1, dy=1):
                return True
        
        # どの一直線上にも配置されていない場合は、player は勝利していないので False を返す
        return False
   
    def is_same(self, mark:str, coord:list[int], dx:int, dy:int) -> bool:
        """指定したマスにマークが配置されているかの判定.
        
        coord のマスから、dx, dy 方向に存在するマスに、
        mark のマークが配置されているかどうかを判定する

        Args:
            mark: 判定するマークを表す文字列
                Marubatsu.CIRCLE または Marubatsu.CROSS を指定する
            coord:
                最初のマスの xy 座標を表す list
            dx:
                次のマスの x 座標の差分
            dy:
                次のマスの y 座標の差分

        Returns:
            すべてのマスに mark のマークが配置されている場合は True
            そうでない場合は False
        """
        
        x, y = coord
        text_list = [self.board[x + i * dx][y + i * dy] 
                     for i in range(self.BOARD_SIZE)]
        line_text = "".join(text_list)
        return line_text == mark * self.BOARD_SIZE

    def is_full(self) -> bool:
        """すべてのマスが埋まっているかどうかの判定.        

        Returns:
            すべてのマスが埋まっている場合は True
            そうでない場合は False
        """
        
        return self.move_count == self.BOARD_SIZE ** 2

    def play(self, ai:list, ai_dict:dict|None=None, params:list[dict]|None=None, names:list[str|None]=None,
             scoretable_dict:dict|None=None, show_subtree:bool=True, show_status:bool=False, verbose:bool=True, seed:bool|None=None, gui:bool=False, size:float=3) -> str | None:
        """〇×ゲームをプレイする.
        
        仮引数 ai でそれぞれの手番の着手を誰が担当するかを指定する
        ゲーム盤が表示されるので、テキストボックスに着手を行う座標を入力する
        座標は x,y の形式で入力する
        返り値として、勝者を表す文字列を返す
        
        Args:
            ai: それぞれの手番を誰が担当するかを指定する list
                0 番の要素が 〇 の手番、1 番の要素が × の手番を表す
                要素に None が代入されている場合は人間が担当することを表す
                要素に関数が代入されている場合は、その関数によって AI が着手を行う
                
                AI の処理を行う関数の仮引数は Marubatsu クラスのインスタンスで、
                着手を行う座標を表す (x, y) の形式の tuple を返すものとする
            ai_dict:
                gui=True の場合に、Dropdown で選択できる AI の一覧を表す dict
                詳細は gui_play の説明を参照すること
            params:
                それぞれの AI に渡すパラメータを要素として持つ list
                パラメータは、マッピング型の展開で AI に渡す
            names:
                GUI で対戦カードを表示する際のそれぞれの AI の名前を表す list 
                要素が None の場合は人間のばあいは "人間"、AI の場合は AI の関数の名前が表示される
            scoretable_dict:
                GUI の部分木の Dropdown に表示する「局面と最善手・評価値の対応表の一覧」のデータを表す dict
            show_subtree:
                True の場合に GUI の部分木を表示する
            show_status:
                True の場合に、現在の局面の状況と、それぞれの合法手に着手した場合の
                局面の状況を表示する
            verbose:
                途中経過を表示するかどうか
                True の場合は途中経過を表示し、False の場合は途中経過を表示しない
            seed:
                None でない場合は、乱数の種をこの値で設定する
                None の場合はなにもしない
            gui:
                False の場合は、入出力を CUI（文字列）で行う
                True の場合は、入出力を GUI（画像）で行う
            size:
                gui が True の場合に描画するゲーム盤の画像のサイズ
                
        Returns:
            gui が True の場合で決着がついていない場合は None
            決着がついた場合または、gui が False の場合は勝者を表す下記のいずれかの文字列
                Marubatsu.CIRCLE: 〇 の勝利
                Marubatsu.CROSS:  × の勝利
                Marubatsu.DRAW:   引き分け
        """

        # params が None の場合のデフォルト値を設定する
        if params is None:
            params = [{}, {}]
            
        # 一部の仮引数をインスタンスの属性に代入する
        self.ai = ai
        self.verbose = verbose
        self.gui = gui
        
        # seed が None でない場合は、seed を乱数の種として設定する
        if seed is not None:
            random.seed(seed)

        # gui が True の場合に、GUI の処理を行う Marubatsu_GUI のインスタンスを作成する
        if gui:
            mb_gui = Marubatsu_GUI(self, params=params, names=names, ai_dict=ai_dict, scoretable_dict=scoretable_dict, 
                                show_subtree=show_subtree, show_status=show_status, seed=seed, size=size)
        else:
            mb_gui = None
            
        self.restart()
        return self.play_loop(mb_gui, params=params)

    def play_loop(self, mb_gui:Marubatsu_GUI|None, params:list[dict]=None) -> str | None:
        """〇×ゲームのゲーム開始後の繰り返し処理を行う.
        
        Args:
            mb_gui:
                GUI の場合は Marubatsu_GUI クラスのインスタンス
                CUI の場合は None
            params:
                それぞれの AI に渡すパラメータを要素として持つ list
                パラメータは、マッピング型の展開で AI に渡す
        Returns:
            決着がついた場合は勝者を表す文字列
            決着がついていない場合は None
        """
        
        if params is None:
            params = [{}, {}]
        
        ai = self.ai
        verbose = self.verbose
        gui = self.gui
        
        # ゲームの決着がついていない間繰り返す
        while self.status == Marubatsu.PLAYING:
            # 現在の手番を表す ai のインデックスを計算する
            index = 0 if self.turn == Marubatsu.CIRCLE else 1
            # ゲーム盤の表示
            if verbose:
                if gui:
                    # AI どうしの対戦の場合は画面を描画しない
                    if ai[0] is None or ai[1] is None:
                        mb_gui.update_gui()
                    # 手番を人間が担当する場合は、play メソッドを終了する
                    if ai[index] is None:
                        return
                else:
                    print(self)
                    
            # ai が着手を行うかどうかを判定する
            if ai[index] is not None:
                x, y = ai[index](self, **params[index])
            else:
                # キーボードからの座標の入力
                coord = input("x,y の形式で座標を入力して下さい。exit を入力すると終了します")
                # "exit" が入力されていればメッセージを表示して関数を終了する
                if coord == "exit":
                    print("ゲームを終了します")
                    return       
                # x 座標と y 座標を要素として持つ list を計算する
                xylist = coord.split(",")
                # xylist の要素の数が 2 ではない場合
                if len(xylist) != 2:
                    # エラーメッセージを表示する
                    print("x, y の形式ではありません")
                    # 残りの while 文のブロックを実行せずに、次の繰り返し処理を行う
                    continue
                x, y = xylist
            # (x, y) に着手を行う
            try:
                self.move(int(x), int(y))
            except:
                print("整数の座標を入力して下さい")

        # 決着がついたので、ゲーム盤を表示する
        if verbose:
            if gui:
                mb_gui.update_gui()
            else:
                print(self)
                
        return self.status
    
    def calc_legal_moves(self) -> list[tuple[int, int]]:
        """合法手の一覧を表す list を計算する.

        Returns:
            合法手の一覧を要素として持つ list
            合法手は座標を表す (x, y) の形式の tuple
        """
        
        if self.status != Marubatsu.PLAYING:
            return []
        legal_moves = [(x, y) for y in range(self.BOARD_SIZE) 
                            for x in range(self.BOARD_SIZE)
                            if self.board[x][y] == Marubatsu.EMPTY]
        return legal_moves
    
    def count_marks(self, coord:list[int], dx:int, dy:int, datatype:str="dict") -> defaultdict | tuple[int, int, int]:
        """指定したマスに配置されている 〇 と × と空のマスの数を数える.
        
        coord のマスから、dx, dy 方向に存在するマスに、
        〇 と × と空のマスの数がそれぞれいくつあるかを数える
        返り値のデータ型を、datatype の値によって、dict と tuple の中から選択できる

        Args:
            coord:
                最初のマスの xy 座標を表す list
            dx:
                次のマスの x 座標の差分
            dy:
                次のマスの y 座標の差分
            datatype:
                "dict"（デフォルト値）の場合に返り値として dict を返す
                それ以外の場合は返り値として tuple を返す

        Returns:
            datatype が "dict" の場合:
                Marubatsu.CIRCLE、Marubatsu.CROSS、Marubatsu.EMPTY をキーとする defaultdict
                それぞれのキーの値は、キーが示すものが配置されているマスの数を表す
            それ以外の場合
                (直前の手番のマークの数、現在の手番のマークの数、空のマスの数) を要素とする tuple
        """    
        
        x, y = coord   
        count = defaultdict(int)
        for _ in range(self.BOARD_SIZE):
            count[self.board[x][y]] += 1
            x += dx
            y += dy

        if datatype == "dict":
            return count
        else:
            return Markpat(count[self.last_turn], count[self.turn], count[Marubatsu.EMPTY])  
    
    def enum_markpats(self) -> set[tuple[int, int, int]]:
        """局面のマークのパターンを列挙する.
        
        Returns:
            局面のマークのパターンを要素として持つ set
            マークのパターンは、`count_marks` によって計算された返り値で
            (直前の手番のマークの数、現在の手番のマークの数、空のマスの数) を要素とする tuple
        """    

        markpats = set()
    
        # 横方向と縦方向の判定
        for i in range(self.BOARD_SIZE):
            count = self.count_marks(coord=[0, i], dx=1, dy=0, datatype="tuple")
            markpats.add(count)
            count = self.count_marks(coord=[i, 0], dx=0, dy=1, datatype="tuple")
            markpats.add(count)
        # 左上から右下方向の判定
        count = self.count_marks(coord=[0, 0], dx=1, dy=1, datatype="tuple")
        markpats.add(count)
        # 右上から左下方向の判定
        count = self.count_marks(coord=[2, 0], dx=-1, dy=1, datatype="tuple")
        markpats.add(count)

        return markpats

    def count_markpats(self) -> defaultdict[tuple[int, int, int], int]:
        """局面のマークのパターンの数を数える.
        
        Returns:
            局面のマークのパターンをキー、マークのパターンの数をキーの値として持つ defaultdict
            マークのパターンは、`count_marks` によって計算された返り値で
            (直前の手番のマークの数、現在の手番のマークの数、空のマスの数) を要素とする tuple
        """    
        
        markpats = defaultdict(int)
        
        if self.count_linemark:
            for countdict in [self.rowcount, self.colcount, self.diacount]:
                for circlecount, crosscount in zip(countdict[Marubatsu.CIRCLE], countdict[Marubatsu.CROSS]):
                    emptycount = self.BOARD_SIZE - circlecount - crosscount
                    if self.last_turn == Marubatsu.CIRCLE:
                        markpats[(circlecount, crosscount, emptycount)] += 1
                    else:
                        markpats[(crosscount, circlecount, emptycount)] += 1
        else:
            # 横方向と縦方向の判定
            for i in range(self.BOARD_SIZE):
                count = self.count_marks(coord=[0, i], dx=1, dy=0, datatype="tuple")
                markpats[count] += 1
                count = self.count_marks(coord=[i, 0], dx=0, dy=1, datatype="tuple")
                markpats[count] += 1
            # 左上から右下方向の判定
            count = self.count_marks(coord=[0, 0], dx=1, dy=1, datatype="tuple")
            markpats[count] += 1
            # 右上から左下方向の判定
            count = self.count_marks(coord=[2, 0], dx=-1, dy=1, datatype="tuple")
            markpats[count] += 1

        return markpats    
           
class Marubatsu_GUI(GUI):
    """ 〇×ゲームの GUI.

    Attributes:
        クラス属性
        mbtree:
            ゲーム盤の下に表示するゲーム木のデータ
    
        インスタンス属性。mb 以外は play メソッドの仮引数と同じ
        mb:
            GUI を表示する Marubatsu ゲームのインスタンス
        mbtree_gui:
            ゲーム盤の下に表示するゲーム木を表示する Mbtree_GUI クラスのインスタンス
        ai (list):
            それぞれの手番を誰が担当するかを指定する list
        ai_dict (dict):
            Dropdown で選択できる AI の一覧を表す dict
        scoretable_dict (dict):
            GUI の部分木の Dropdown に表示する「局面と最善手・評価値の対応表の一覧」のデータを表す dict
        seed (int|None):
            乱数の種
        size (int):
            gui が True の場合に描画するゲーム盤の画像のサイズ
    """
    
    def __init__(self, mb:Marubatsu, params:list|None, names:list|None, ai_dict:dict|None,
                 scoretable_dict:dict|None, show_subtree:bool, show_status:bool, seed:int, size:int):
        """ GUI のウィジェットの作成などの初期設定を行う.
        
        Args:
            Marubatsu_GUI の属性と同じ
        """
        
        if params is None:
            params = [{}, {}]
        if ai_dict is None:
            ai_dict = {}
        if names is None:
            names = [None, None]
        for i in range(2):
            if names[i] is None:
                if mb.ai[i] is None:
                    names[i] = "人間"
                else:
                    names[i] = mb.ai[i].__name__
        
        # JupyterLab からファイルダイアログを開く際に必要な前処理
        root = Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)  

        # save フォルダが存在しない場合は作成する
        if not os.path.exists("save"):
            os.mkdir("save")        
        
        self.mb = mb
        self.ai_dict = ai_dict
        self.params = params
        self.names = names
        self.show_subtree = show_subtree
        self.show_status = show_status
        self.seed = seed
        self.size = size
        
        from util import load_bestmoves

        self.score_table = load_bestmoves("../data/bestmoves_and_score_by_board.dat")
        
        super(Marubatsu_GUI, self).__init__()
        
        from tree import Mbtree_GUI

        self.mbtree_gui = Mbtree_GUI(scoretable_dict, size=0.1)  
                   
    def create_dropdown(self):
        """AI を選択する Dropdown を作成する."""
 
        # それぞれの手番の担当を表す Dropdown の項目の値を記録する list を初期化する
        select_values = []
        # 〇 と × の Dropdown を格納する list
        self.dropdown_list = []
        # ai に代入されている内容を ai_dict に追加する
        for i in range(2):
            value = ( self.mb.ai[i], self.params[i] )
            # value を select_values に常に登録する
            select_values.append(value)
            # value が ai_values に登録済かどうかを判定する
            if value not in self.ai_dict.values():
                # 項目を登録する
                self.ai_dict[self.names[i]] = value

        for i in range(2):
            # Dropdown の description を計算する
            description = "〇" if i == 0 else "×"
            self.dropdown_list.append(
                widgets.Dropdown(
                    options=self.ai_dict,
                    description=description,
                    layout=widgets.Layout(width="100px"),
                    style={"description_width": "20px"},
                    value=select_values[i],
                )
            ) 
                
        self.status_ai_dict = self.ai_dict.copy()
        self.status_ai_dict["手番の AI"] = ("Auto", None)
        self.status_dropdown = widgets.Dropdown(
            options=self.status_ai_dict,
            layout=widgets.Layout(width="100px"),
            style={"description_width": "20px"},
            value=select_values[0],
        )   
               
    def create_figure(self):
        """ゲーム盤を描画する Figure を作成する."""
        
        with plt.ioff():
            self.fig, self.ax = plt.subplots(figsize=[self.size, self.size])
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False     
        
    def create_widgets(self):
        """ウィジェットを作成する."""
  
        # 乱数の種の Checkbox と IntText を作成する
        self.checkbox = widgets.Checkbox(value=self.seed is not None, description="乱数の種",
                                        indent=False, layout=widgets.Layout(width="100px"))
        self.inttext = widgets.IntText(value=0 if self.seed is None else self.seed,
                                    layout=widgets.Layout(width="80px"))   

        # 読み書き、ヘルプのボタンを作成する
        self.load_button = self.create_button("開く", 50)
        self.save_button = self.create_button("保存", 50)
        self.show_tree_button = self.create_button("木", 34)
        self.reset_tree_button = self.create_button("リ", 34)
        self.help_button = self.create_button("？", 34)

        # 状況ボタン、大きさを変更する FloatSlider を作成する        
        self.show_status_button = self.create_button("状況", 50)
        self.size_slider = widgets.FloatSlider(min=1.0, max=5.0, step=0.1,
                                            description="size", value=self.size)
        
        # AI を選択する Dropdown を作成する
        self.create_dropdown()
        # 変更、リセット、待ったボタンを作成する
        self.change_button = self.create_button("変更", 50)
        self.reset_button = self.create_button("リセット", 80)
        self.undo_button = self.create_button("待った", 60)    
        
        # リプレイのボタンとスライダーを作成する
        self.first_button = self.create_button("<<", 50)
        self.prev_button = self.create_button("<", 50)
        self.next_button = self.create_button(">", 50)
        self.last_button = self.create_button(">>", 50)     
        self.slider = widgets.IntSlider(layout=widgets.Layout(width="200px"))
        # ゲーム盤の画像を表す figure を作成する
        self.create_figure()

        # print による文字列を表示する Output を作成する
        self.output = widgets.Output()       
        
        # ヘルプを表示する Output を作成し、表示の設定を行う
        self.help = widgets.Output()
        self.print_helpmessage()
        self.help.layout.display = "none"    

        self.output = widgets.Output()  
        self.print_helpmessage()
        self.output.layout.display = "none"
        
    def print_helpmessage(self):
        """ヘルプのメッセージを表示する"""
        
        with self.help:
            print("""操作説明

        マスの上でクリックすることで着手を行う。
        下記の GUI で操作を行うことができる。
        ()が記載されているものは、キー入力で同じ操作を行うことができることを意味する。
        なお、キー入力の操作は、ゲーム盤をクリックして選択状態にする必要がある。

        乱数の種\tチェックボックスを ON にすると、右のテキストボックスの乱数の種が適用される
        開く(-,L)\tファイルから対戦データを読み込む
        保存(+,S)\tファイルに対戦データを保存する
        木\t下部の GUI の部分木を表示の有無を切り替える
        リ\r株の GUI の部分木の中心となるノードを、現在の局面にリセットする
        ？(*,H)\t\tこの操作説明を表示する
        手番の担当\tメニューからそれぞれの手番の担当を選択する
        \t\tメニューから選択しただけでは担当は変更されず、変更またはリセットボタンによって担当が変更される
        変更\t\tゲームの途中で手番の担当を変更する
        リセット\t手番の担当を変更してゲームをリセットする
        待った(0)\t1つ前の自分の着手をキャンセルする
        <<(↑)\t\t最初の局面に移動する
        <(←)\t\t1手前の局面に移動する
        >(→)\t\t1手後の局面に移動する
        >>(↓)\t\t最後の着手が行われた局面に移動する
        スライダー\t現在の手数を表す。ドラッグすることで任意の手数へ移動する

        手数を移動した場合に、最後の着手が行われた局面でなければ、リプレイモードになる。
        リプレイモード中に着手を行うと、リプレイモードが解除され、その着手が最後の着手になる。""")
    
    def display_widgets(self):
        """ ウィジェットを配置して表示する."""

        # 乱数の種のウィジェット、読み書き、ヘルプのボタンを横に配置した HBox を作成する
        hbox1 = widgets.HBox([self.checkbox, self.inttext, self.load_button, self.save_button, 
                            self.show_tree_button, self.reset_tree_button, self.help_button])
        # 状況ボタンとゲーム盤のサイズの変更の FloatSlider を配置した HBox を作成する
        hbox2 = widgets.HBox([self.show_status_button, self.status_dropdown, self.size_slider])
        # 〇 と × の dropdown とボタンを横に配置した HBox を作成する
        hbox3 = widgets.HBox([self.dropdown_list[0], self.dropdown_list[1], self.change_button, self.reset_button, self.undo_button])
        # リプレイ機能のボタンを横に配置した HBox を作成する
        hbox4 = widgets.HBox([self.first_button, self.prev_button, self.next_button, self.last_button, self.slider]) 
        # hbox1 ~ hbox4、Figure、Output を縦に配置した VBox を作成し、表示する
        display(widgets.VBox([hbox1, hbox2, hbox3, hbox4, self.fig.canvas, self.output, self.help]))

    def update_widgets_status(self):
        """ウィジェットの状態を更新する."""
        
        self.inttext.disabled = not self.checkbox.value
        self.set_button_color(self.show_tree_button, self.show_subtree)    
        self.set_button_status(self.reset_tree_button, not self.show_subtree)    
        self.set_button_color(self.show_status_button, self.show_status)    
        self.set_button_status(self.undo_button, self.mb.move_count < 2 or self.mb.move_count != len(self.mb.records) - 1)
        self.set_button_status(self.first_button, self.mb.move_count <= 0)
        self.set_button_status(self.prev_button, self.mb.move_count <= 0)
        self.set_button_status(self.next_button, self.mb.move_count >= len(self.mb.records) - 1)
        self.set_button_status(self.last_button, self.mb.move_count >= len(self.mb.records) - 1)    
        # value 属性よりも先に max 属性に値を代入する必要がある点に注意！
        self.slider.max = len(self.mb.records) - 1
        self.slider.value = self.mb.move_count
       
    def create_event_handler(self):
        """イベントハンドラを定義し、ウィジェットに結び付ける."""
 
        # 乱数の種のチェックボックスのイベントハンドラを定義する
        def on_checkbox_changed(changed):
            self.update_widgets_status()
            
        self.checkbox.observe(on_checkbox_changed, names="value")

        # 開く、保存ボタンのイベントハンドラを定義する
        def on_load_button_clicked(b=None):
            path = filedialog.askopenfilename(filetypes=[("〇×ゲーム", "*.mbsav")],
                                            initialdir="save")
            if path != "":
                with open(path, "rb") as f:
                    data = pickle.load(f)
                    self.mb.records = data["records"]
                    self.mb.ai = data["ai"]
                    self.params = data["params"] if "params" in data else [ {}, {} ]
                    if "names" in data:
                        names = data["names"]
                    else:
                        names = [ "人間" if self.mb.ai[i] is None else self.mb.ai[i].__name__ for i in range(2)]                       
                    options = self.dropdown_list[0].options.copy()
                    for i in range(2):
                        value = (self.mb.ai[i], self.params[i]) 
                        if not value in options.values():
                            options[names[i]] = value
                    for i in range(2):
                        self.dropdown_list[i].options = options
                        self.dropdown_list[i].value = (self.mb.ai[i], self.params[i])            
                    status_options = options.copy()
                    status_options["手番の AI"] = ("Auto", None)
                    self.status_dropdown.options = status_options
                    change_step(data["move_count"])
                    if data["seed"] is not None:                   
                        self.checkbox.value = True
                        self.inttext.value = data["seed"]
                    else:
                        self.checkbox.value = False
                        
        def on_save_button_clicked(b=None):
            names = [ self.dropdown_list[i].label for i in range(2) ]     
            timestr = datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒")
            fname = f"{names[0]} VS {names[1]} {timestr}"
            path = filedialog.asksaveasfilename(filetypes=[("〇×ゲーム", "*.mbsav")],
                                                initialdir="save", initialfile=fname,
                                                defaultextension="mbsav")
            if path != "":
                with open(path, "wb") as f:
                    data = {
                        "records": self.mb.records,
                        "move_count": self.mb.move_count,
                        "ai": self.mb.ai,
                        "params": self.params,
                        "names": names,
                        "seed": self.inttext.value if self.checkbox.value else None
                    }
                    pickle.dump(data, f)
                    
        def on_show_tree_button_clicked(b=None):
            self.show_subtree = not self.show_subtree
            self.mbtree_gui.vbox.layout.display = None if self.show_subtree else "none"
            self.update_gui()
            
        def on_reset_tree_button_clicked(b=None):
            self.update_gui()
                    
        def on_help_button_clicked(b=None):
            self.help.layout.display = "none" if self.help.layout.display is None else None

        self.load_button.on_click(on_load_button_clicked)
        self.save_button.on_click(on_save_button_clicked)
        self.show_tree_button.on_click(on_show_tree_button_clicked)
        self.reset_tree_button.on_click(on_reset_tree_button_clicked)
        self.help_button.on_click(on_help_button_clicked)
        
        def on_show_status_button_clicked(b=None):
            self.show_status = not self.show_status
            self.update_gui()

        def on_status_dropdown_changed(changed):
            self.update_gui()

        def on_size_slider_changed(changed):
            self.size = changed["new"]
            self.fig.set_figwidth(self.size)
            self.fig.set_figheight(self.size)
            self.update_gui()

        self.show_status_button.on_click(on_show_status_button_clicked)
        self.status_dropdown.observe(on_status_dropdown_changed, names="value")
        self.size_slider.observe(on_size_slider_changed, names="value")

        # 変更ボタンのイベントハンドラを定義する
        def on_change_button_clicked(b):
            for i in range(2):
                self.mb.ai[i], self.params[i] = self.dropdown_list[i].value
            self.mb.play_loop(self, self.params)

        # リセットボタンのイベントハンドラを定義する
        def on_reset_button_clicked(b=None):
            # 乱数の種のチェックボックスが ON の場合に、乱数の種の処理を行う
            if self.checkbox.value:
                random.seed(self.inttext.value)
            self.mb.restart()
            self.output.clear_output()
            on_change_button_clicked(b)

        # 待ったボタンのイベントハンドラを定義する
        def on_undo_button_clicked(b=None):
            if self.mb.move_count >= 2 and self.mb.move_count == len(self.mb.records) - 1:
                self.mb.move_count -= 2
                self.mb.records = self.mb.records[0:self.mb.move_count+1]
                self.mb.change_step(self.mb.move_count)
                self.update_gui()
            
        # イベントハンドラをボタンに結びつける
        self.change_button.on_click(on_change_button_clicked)
        self.reset_button.on_click(on_reset_button_clicked)   
        self.undo_button.on_click(on_undo_button_clicked)   

        # step 手目の局面に移動する
        def change_step(step):
            self.mb.change_step(step)
            # 描画を更新する
            self.update_gui()        

        def on_first_button_clicked(b=None):
            change_step(0)

        def on_prev_button_clicked(b=None):
            change_step(self.mb.move_count - 1)

        def on_next_button_clicked(b=None):
            change_step(self.mb.move_count + 1)
            
        def on_last_button_clicked(b=None):
            change_step(len(self.mb.records) - 1)

        def on_slider_changed(changed):
            if self.mb.move_count != changed["new"]:
                change_step(changed["new"])
            
        self.first_button.on_click(on_first_button_clicked)
        self.prev_button.on_click(on_prev_button_clicked)
        self.next_button.on_click(on_next_button_clicked)
        self.last_button.on_click(on_last_button_clicked)
        self.slider.observe(on_slider_changed, names="value")

        # ゲーム盤の上でマウスを押した場合のイベントハンドラ
        def on_mouse_down(event):
            # Axes の上でマウスを押していた場合のみ処理を行う
            if event.inaxes and self.mb.status == Marubatsu.PLAYING:
                x = math.floor(event.xdata)
                y = math.floor(event.ydata)
                with self.output:
                    self.mb.move(x, y)                
                # 次の手番の処理を行うメソッドを呼び出す
                    self.mb.play_loop(self, self.params)

        # ゲーム盤を選択した状態でキーを押した場合のイベントハンドラ
        def on_key_press(event):
            keymap = {
                "up": on_first_button_clicked,
                "left": on_prev_button_clicked,
                "right": on_next_button_clicked,
                "down": on_last_button_clicked,
                "0": on_undo_button_clicked,
                "enter": on_reset_button_clicked,            
                "-": on_load_button_clicked,            
                "l": on_load_button_clicked,            
                "+": on_save_button_clicked,            
                "s": on_save_button_clicked,            
                "*": on_help_button_clicked,            
                "h": on_help_button_clicked,            
            }
            if event.key in keymap:
                keymap[event.key]()
            else:
                try:
                    num = int(event.key) - 1
                    event.inaxes = True
                    event.xdata = num % 3
                    event.ydata = 2 - (num // 3)
                    on_mouse_down(event)
                except:
                    pass
                
        # fig の画像イベントハンドラを結び付ける
        self.fig.canvas.mpl_connect("button_press_event", on_mouse_down)     
        self.fig.canvas.mpl_connect("key_press_event", on_key_press)           

    @staticmethod
    def draw_mark(ax, x:int, y:int, mark:str, color:str="black", lw:float=2):
        """マークを描画する.
        
        (x, y) のマスに、mark で指定したマークの画像を color で指定した色で描画する
        
        Args:
            ax:
                マークを描画する Axes
            x:
                マークを描画する、ゲーム盤の x 座標
            y:
                マークを描画する、ゲーム盤の y 座標
            mark:
                描画するマーク
            color:
                描画するマークの色
            lw:
                描画する図形の線の太さ
        """    
        
        if mark == Marubatsu.CIRCLE:
            circle = patches.Circle([x + 0.5, y + 0.5], 0.35, ec=color, fill=False, lw=lw)
            ax.add_artist(circle)
        elif mark == Marubatsu.CROSS:
            ax.plot([x + 0.15, x + 0.85], [y + 0.15, y + 0.85], c=color, lw=lw)
            ax.plot([x + 0.15, x + 0.85], [y + 0.85, y + 0.15], c=color, lw=lw)
    
    @staticmethod
    def draw_board(ax, mb:Marubatsu, show_result:bool=False, score:float|None=None, bc:None|str=None, bw:float=1, darkness:float=0, dx:float=0, dy:float=0, lw:float=2):
        """ゲーム盤を描画する
        
        Args:
            ax:
                ゲーム盤を描画する Axes
            mb:
                ゲーム盤を表す Marubatsu クラスのインスタンス
            show_result:
                決着がついているか、score が None でない場合に、背景色を変えて描画する
            score:
                その局面の評価値
            bc:
                枠の色。None の場合は枠を描画しない
            bw:
                枠の太さ
            darkness:
                表示の暗さを表す 0 ～ 1 の数値。大きいほど暗く表示する
            dx:
                描画するゲーム盤の左上の点の Axes の x 座標
            dy:
                描画するゲーム盤の左上の点の Axes の y 座標
            lw:
                描画する図形の線の太さ
        """
        
        # 結果によってゲーム盤の背景色を変更する
        if show_result:
            if score is None and mb.status == Marubatsu.PLAYING:
                bgcolor = "white"
            elif (score is not None and score >= 1) or mb.status == Marubatsu.CIRCLE:
                bgcolor = "lightcyan"
            elif (score is not None and score <= -1) or mb.status == Marubatsu.CROSS:
                bgcolor = "lavenderblush"
            else:
                bgcolor = "lightyellow"      
                
            rect = patches.Rectangle(xy=(dx, dy), width=mb.BOARD_SIZE,
                                    height=mb.BOARD_SIZE, fc=bgcolor)
            ax.add_patch(rect)

        # ゲーム盤の枠を描画する
        for i in range(1, mb.BOARD_SIZE):
            ax.plot([dx, dx + mb.BOARD_SIZE], [dy + i, dy + i], c="k", lw=lw) # 横方向の枠線
            ax.plot([dx + i, dx + i], [dy, dy + mb.BOARD_SIZE], c="k", lw=lw) # 縦方向の枠線

        # ゲーム盤のマークを描画する
        for y in range(mb.BOARD_SIZE):
            for x in range(mb.BOARD_SIZE):
                color = "red" if (x, y) == mb.last_move else "black"
                Marubatsu_GUI.draw_mark(ax, dx + x, dy + y, mb.board[x][y], color, lw=lw)

        # darkness 0 より大きい場合は、半透明の黒い正方形を描画して暗くする
        if darkness > 0:
            ax.add_artist(patches.Rectangle(xy=(dx, dy), width=mb.BOARD_SIZE,
                                            height=mb.BOARD_SIZE, fc="black", alpha=darkness))

        # bc が None でない場合はその色で bw の太さで外枠を描画する
        if bc is not None:
            frame = patches.Rectangle(xy=(dx, dy), width=mb.BOARD_SIZE,
                                    height=mb.BOARD_SIZE, ec=bc, fill=False, lw=bw)
            ax.add_patch(frame)
                               
    def update_gui(self):
        """GUI の表示や設定を更新する"""
        
        def calc_status_txt(score):
            if score > 0:
                return "〇"
            elif score == 0:
                return "△"
            else:
                return "×"
        
        ax = self.ax

        # Axes の内容をクリアして、これまでの描画内容を削除する
        ax.clear()

        # y 軸を反転させる
        ax.invert_yaxis()

        # 枠と目盛りを表示しないようにする
        ax.axis("off")   

        # リプレイ中、ゲームの決着がついていた場合は背景色を変更する
        is_replay =  self.mb.move_count < len(self.mb.records) - 1 
        if self.mb.status == Marubatsu.PLAYING:
            facecolor = "lightcyan" if is_replay else "white"
        else:
            facecolor = "lightyellow"

        ax.figure.set_facecolor(facecolor)
            
        # 上部のメッセージを描画する
        # 対戦カードの文字列を計算する
        ax.text(1.5, 3.5, f"{self.dropdown_list[0].label}　VS　{self.dropdown_list[1].label}", 
                fontsize=7*self.size, ha="center")   

        # ゲームの決着がついていない場合は、手番を表示する
        if self.mb.status == Marubatsu.PLAYING:
            text = "Turn " + self.mb.turn
            score = self.score_table[self.mb.board_to_str()]["score"]
            if self.show_status:
                text += " 状況 " + calc_status_txt(score)
        # 引き分けの場合
        elif self.mb.status == Marubatsu.DRAW:
            text = "Draw game"
        # 決着がついていれば勝者を表示する
        else:
            text = "Winner " + self.mb.status
        # リプレイ中の場合は "Replay" を表示する
        if is_replay:
            text += " Replay"
        ax.text(1.5, -0.2, text, fontsize=7*self.size, ha="center")

        self.draw_board(ax, self.mb, lw=0.7*self.size)
        
        if self.show_status:
            bestmoves = self.score_table[self.mb.board_to_str()]["bestmoves"]
            ai, params = self.status_dropdown.value
            if ai == "Auto":
                index = 0 if self.mb.turn == Marubatsu.CIRCLE else 1
                ai = self.mb.ai[index]
                params = self.params[index]
            if ai is not None:
                analyze = ai(self.mb, analyze=True, **params)
                score_by_move = analyze["score_by_move"]
                candidate = analyze["candidate"]
            for move in self.mb.calc_legal_moves():
                x, y = move
                mb = deepcopy(self.mb)
                mb.move(x, y)
                score = self.score_table[mb.board_to_str()]["score"]
                color = "red" if move in bestmoves else "black"
                text = calc_status_txt(score)
                ax.text(x + 0.1, y + 0.35, text, fontsize=5*self.size, c=color)
                if ai is not None:
                    if score_by_move is not None:
                        color = "red" if move in candidate else "black"
                        ax.text(x + 0.1, y + 0.65, score_by_move[move], fontsize=5*self.size, c=color)
                    elif move in candidate:
                        ax.text(x + 0.1, y + 0.65, "候補手", fontsize=4.8*self.size)
                    
        self.update_widgets_status()

        if hasattr(self, "mbtree_gui"):
            from tree import Node

            self.mbtree_gui.selectednode = Node(self.mb, depth=self.mb.move_count)
            self.mbtree_gui.update_gui()