def initialize_board():
    return [[" "] * 3 for x in range(3)]

def place_mark(board, x, y, mark):
    if board[x][y] == " ":
        board[x][y] = mark
    else:
        print("(", x, ",", y, ") のマスにはマークが配置済です")