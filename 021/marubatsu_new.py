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
            空白のマスは " "、〇 のマスは "o"、× のマスは "x" を代入する
    """

    EMPTY = "."
    CIRCLE = "o"
    CROSS = "x"
    
    def __init__(self, board_size=3):
        """ イニシャライザ. 
        
        Args:
            size (int):
                ゲーム盤の縦横のサイズを表す整数
        """

        self.BOARD_SIZE = board_size
        self.initialize_board()
        
    def initialize_board(self):
        """ ゲーム盤のデータの初期化を行うメソッド. """
        
        self.board = [[Marubatsu.EMPTY] * self.BOARD_SIZE for y in range(self.BOARD_SIZE)]    

    def set_mark(self, x, y, mark):
        """ ゲーム盤の指定したマスに指定したマークを配置するメソッド.

        (x, y) のマスに mark で指定したマークを配置する.
        (x, y) のマスに既にマークが配置済の場合は、メッセージを表示する.

        Args:
            x (int):
                マークを配置するマスの x 座標
            y (int):
                マークを配置するマスの y 座標
            mark (str):
                配置するマークを表す文字列
        """

        if self.board[x][y] == Marubatsu.EMPTY:
            self.board[x][y] = mark
        else:
            print("(", x, ",", y, ") のマスにはマークが配置済です")

    def display_board(self):   
        """ ゲーム盤を表示するメソッド. """

        # 各行に対する繰り返しの処理を行う
        for y in range(self.BOARD_SIZE):
            # y 行の各マスに対する繰り返しの処理を行う
            for x in range(self.BOARD_SIZE):
                # (x, y) のマスの要素を改行せずに表示する
                print(self.board[x][y], end="")
            # x 列の表示が終わったので、改行する
            print()  