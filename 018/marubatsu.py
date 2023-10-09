def initialize_board() -> list[list[str]]:
    """ 初期化されたゲーム盤のデータを返す.

    Returns:
        初期化されたゲーム盤を表す 2 次元配列の list.
        全ての要素に半角の空白文字が代入されている.
    """

    return [[" "] * 3 for y in range(3)]

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

    if board[x][y] == " ":
        board[x][y] = mark
    else:
        print("(", x, ",", y, ") のマスにはマークが配置済です")