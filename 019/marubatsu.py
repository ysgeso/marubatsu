def initialize_board() -> list[list[str]]:
    """ 初期化されたゲーム盤のデータを返す.

    Returns:
        初期化されたゲーム盤を表す 2 次元配列の list.
        全ての要素に半角の "." が代入されている.
    """

    return [["."] * 3 for x in range(3)]

def place_mark(board: list[list[str]], x: int, y: int , mark: str):
    """ ゲーム盤の指定したマスに指定したマークを配置する.

    (x, y) のマスに mark で指定したマークを配置する.
    (x, y) のマスに既にマークが配置済の場合は、メッセージを表示する.

    Args:
        board:
            マークを配置する、ゲーム盤を表す 2 次元配列の list
        x:
            マークを配置するマスの x 座標
        y:
            マークを配置するマスの y 座標
        mark:
            配置するマークを表す文字列
    """

    if board[x][y] == ".":
        board[x][y] = mark
    else:
        print("(", x, ",", y, ") のマスにはマークが配置済です")
        
def display_board(board: list[list[str]]):
    """ ゲーム盤を表示する.
    
    Args:
        board:
            表示するゲーム盤を表す 2 次元配列の list
    """
    
    # 各行に対する繰り返しの処理を行う
    for y in range(3):
        # y 行の各マスに対する繰り返しの処理を行う
        for x in range(3):
            # (x, y) のマスの要素を改行せずに表示する
            print(board[x][y], end="")
        # y 行の表示が終わったので、改行する
        print()        
