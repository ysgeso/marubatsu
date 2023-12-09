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
    """

    EMPTY = "."
    CIRCLE = "o"
    CROSS = "x"
    DRAW = "draw"
    PLAYING = "playing"
    
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
            
    def judge(self) -> str:
        """ 勝敗判定.
        
        Returns:
            以下のいずれかの値を返す
            Marubatsu.CIRCLE:  〇 の勝利
            Marubatsu.CROSS:   × の勝利
            Marubatsu.DRAW:    引き分け
            Marubatsu.PLAYING: 決着がついていない
        """
        
        # 〇 の勝利の判定
        if self.is_winner(Marubatsu.CIRCLE):
            return Marubatsu.CIRCLE
        # × の勝利の判定
        elif self.is_winner(Marubatsu.CROSS):
            return Marubatsu.CROSS   
        # 引き分けの判定
        elif not(self.board[0][0] == Marubatsu.EMPTY or \
            self.board[1][0] == Marubatsu.EMPTY or \
            self.board[2][0] == Marubatsu.EMPTY or \
            self.board[0][1] == Marubatsu.EMPTY or \
            self.board[1][1] == Marubatsu.EMPTY or \
            self.board[2][1] == Marubatsu.EMPTY or \
            self.board[0][2] == Marubatsu.EMPTY or \
            self.board[1][2] == Marubatsu.EMPTY or \
            self.board[2][2] == Marubatsu.EMPTY):
            return Marubatsu.DRAW
        # 上記のどれでもなければ決着がついていない
        else:
            return Marubatsu.PLAYING            
            
    def __str__(self):
        text = "Turn " + self.turn + "\n"
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                text += self.board[x][y]
            text += "\n"
        return text
    
    def is_winner(self, winner:str) -> bool:
        """winner のプレイヤーの勝利判定.

        Args:
            winner: 
                判定するプレイヤーを表す文字列
                Marubatsu.CIRCLE または Marubatsu.CROSS を指定する

        Returns:
            winner のプレイヤーが勝利している場合は True
            そうでない場合は False
        """
        # 一直線上のマスの座標を作成するためのデータを集めた list を代入する変数を空の list で初期化する
        judge_data_list = []
        # 縦方向の座標を作成するために必要なデータを追加する
        for y in range(self.BOARD_SIZE):
            judge_data_list.append({ "coord": [0, y], "dx": 1, "dy": 0 })
        # 横方向の座標を作成するために必要なデータを追加する
        for x in range(self.BOARD_SIZE):
            judge_data_list.append({ "coord": [x, 0], "dx": 0, "dy": 1 })
        # 左上から右下方向の座標を追加する
        judge_data_list.append({ "coord": [0, 0], "dx": 1, "dy": 1 })
        # 右上から左下方向の座標を追加する
        judge_data_list.append({ "coord": [2, 0], "dx": -1, "dy": 1 })     

        # 一直線上のマスの座標作成するためのデータを順番に取り出す繰り返し処理
        for judge_data in judge_data_list:
            # 取り出した一直線上のマスに winner が配置されているかどうかを判定する
            if self.is_same(winner, **judge_data):
                # 並んでいれば winner の勝利なので True を返す
                return True

        # どの一直線上にも配置されていない場合は、winner は勝利していないので False を返す
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
        for _ in range(self.BOARD_SIZE):
            if self.board[x][y] != mark:
                return False
            x += dx
            y += dy

        return True