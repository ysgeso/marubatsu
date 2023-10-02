class Marubatsu:
    """ 〇×ゲーム

    Attributes:
        クラス属性:
        EMPTY (str):
            空のマスを表す文字列
        CIRCLE (str):
            〇のマスを表す文字列
        CROSS (str):
            ×のマークを表す文字列
            
        インスタンス属性:
        BOARD_SIZE (int):
            ゲーム盤の縦横のサイズを表す整数
        board (list[list[str]):
            ゲーム盤を表す 2 次元配列の list
            2 つのインデックスは、順に x 座標、y 座標を表す
            空白のマスは " "、〇 のマスは CIRCLE、× のマスは CROSS を代入する
        turn (str):
            手番を表す文字列。〇 の手番は CIRCLE、× の手番は CROSS を代入する
    """

    EMPTY = "."
    CIRCLE = "o"
    CROSS = "x"
    
    def __init__(self, board_size: int = 3):
        """ イニシャライザ. 
        
        Args:
            size (int):
                ゲーム盤の縦横のサイズを表す整数
        """

        self.BOARD_SIZE = board_size
        self.restart()
        
    def initialize_board(self):
        """ ゲーム盤のデータの初期化を行うメソッド. """
        
        self.board = [[Marubatsu.EMPTY] * self.BOARD_SIZE for y in range(self.BOARD_SIZE)]    
        
        
    def restart(self):
        """ 〇×ゲームを再起動するメソッド """

        self.initialize_board()
        self.turn = Marubatsu.CIRCLE        

    def place_mark(self, x: int, y: int, mark: str) -> bool:
        """ ゲーム盤の指定したマスに指定したマークを配置するメソッド.

        (x, y) のマスに mark で指定したマークを配置する.
        (x, y) のマスに既にマークが配置済の場合は、メッセージを表示する.
        マークを配置できた場合は True を、配置できなかった場合は False を返す

        Args:
            x (int):
                マークを配置するマスの x 座標
            y (int):
                マークを配置するマスの y 座標
            mark (str):
                配置するマークを表す文字列
                
        Returns:
            bool: マークを配置できた場合は True、配置できなかった場合は False
        """

        if self.board[x][y] == Marubatsu.EMPTY:
            self.board[x][y] = mark
        else:
            print("(", x, ",", y, ") のマスにはマークが配置済です")
            
    def move(self, x: int, y: int):
        self.place_mark(x, y, self.turn)
        if self.turn == Marubatsu.CIRCLE:
            self.turn = Marubatsu.CROSS
        else:
            self.turn = Marubatsu.CIRCLE              
            
    def __str__(self):
        text = "Turn " + self.turn + "\n"
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                text += self.board[x][y]
            text += "\n"
        return text