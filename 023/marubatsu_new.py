# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations

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
        
        インスタンス属性
        BOARD_SIZE (int):
            ゲーム盤の縦横のサイズを表す数値
        board (list[list[str]):
            ゲーム盤を表す 2 次元配列の list
            2 つのインデックスは、順に x 座標、y 座標を表す
            空白のマスは " "、〇 のマスは "o"、× のマスは "x" を代入する
    """

    EMPTY = "."
    CIRCLE = "o"
    CROSS = "x"
    
    def __init__(self, board_size: int=3):
        """ イニシャライザ 
        
        Args:
            board_size:
                ゲーム盤の縦横のサイズ。デフォルト値は 3
        """

        # ゲーム盤の縦横のサイズ
        self.BOARD_SIZE = board_size
        # 〇×ゲーム盤を再起動するメソッドを呼び出す
        self.restart()

    def initialize_board(self):
        """ ゲーム盤のデータの初期化. """

        self.board = [[Marubatsu.EMPTY] * self.BOARD_SIZE for y in range(self.BOARD_SIZE)]

    def place_mark(self, x: int, y: int, mark: str) -> bool:
        """ ゲーム盤の指定したマスに指定したマークを配置する.

        (x, y) のマスに mark で指定したマークを配置する.
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

        if self.board[x][y] == Marubatsu.EMPTY:
            self.board[x][y] = mark
            return True
        else:
            print("(", x, ",", y, ") のマスにはマークが配置済です")
            return False
            
    def restart(self):
        """ 〇×ゲームを再起動する. """
        self.initialize_board()
        self.turn = Marubatsu.CIRCLE            
            
    def move(self, x: int, y: int):
        """ ゲーム盤の指定したマスに着手する.

        Args:
            x:
                マークを配置するマスの x 座標
            y:
                マークを配置するマスの y 座標
        """
        if self.place_mark(x, y, self.turn):
            self.turn = Marubatsu.CROSS if self.turn == Marubatsu.CIRCLE else Marubatsu.CIRCLE  
            
    def judge(self) -> str | None:
        # 判定を行う前に、決着がついていないことにしておく
        winner = None
        # 〇 の勝利の判定
        if self.board[0][0] == self.board[1][0] == self.board[2][0] == Marubatsu.CIRCLE or \
        self.board[0][1] == self.board[1][1] == self.board[2][1] == Marubatsu.CIRCLE or \
        self.board[0][2] == self.board[1][2] == self.board[2][2] == Marubatsu.CIRCLE or \
        self.board[0][0] == self.board[0][1] == self.board[0][2] == Marubatsu.CIRCLE or \
        self.board[1][0] == self.board[1][1] == self.board[1][2] == Marubatsu.CIRCLE or \
        self.board[2][0] == self.board[2][1] == self.board[2][2] == Marubatsu.CIRCLE or \
        self.board[0][0] == self.board[1][1] == self.board[2][2] == Marubatsu.CIRCLE or \
        self.board[2][0] == self.board[1][1] == self.board[0][2] == Marubatsu.CIRCLE:
            winner = Marubatsu.CIRCLE
            
        # × の勝利の判定
        if self.board[0][0] == self.board[1][0] == self.board[2][0] == Marubatsu.CROSS or \
        self.board[0][1] == self.board[1][1] == self.board[2][1] == Marubatsu.CROSS or \
        self.board[0][2] == self.board[1][2] == self.board[2][2] == Marubatsu.CROSS or \
        self.board[0][0] == self.board[0][1] == self.board[0][2] == Marubatsu.CROSS or \
        self.board[1][0] == self.board[1][1] == self.board[1][2] == Marubatsu.CROSS or \
        self.board[2][0] == self.board[2][1] == self.board[2][2] == Marubatsu.CROSS or \
        self.board[0][0] == self.board[1][1] == self.board[2][2] == Marubatsu.CROSS or \
        self.board[2][0] == self.board[1][1] == self.board[0][2] == Marubatsu.CROSS:
            winner = Marubatsu.CROSS     

        # 引き分けの判定
        if not(self.board[0][0] == Marubatsu.EMPTY or \
            self.board[1][0] == Marubatsu.EMPTY or \
            self.board[2][0] == Marubatsu.EMPTY or \
            self.board[0][1] == Marubatsu.EMPTY or \
            self.board[1][1] == Marubatsu.EMPTY or \
            self.board[1][1] == Marubatsu.EMPTY or \
            self.board[0][2] == Marubatsu.EMPTY or \
            self.board[1][2] == Marubatsu.EMPTY or \
            self.board[2][2] == Marubatsu.EMPTY):
            winner = Marubatsu.DRAW

        # winner を返り値として返す
        return winner            
            
    def __str__(self):
        text = "Turn " + self.turn + "\n"
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                text += self.board[x][y]
            text += "\n"
        return text