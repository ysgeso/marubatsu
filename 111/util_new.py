from marubatsu import Marubatsu
import ai as ai_module
import pickle
import gzip
from tqdm import tqdm

def gui_play(ai=None, ai_dict=None, seed:int|None=None):
    """GUI で 〇×ゲームを遊ぶ
    
        Marubatsu クラスのインスタンスを作成し、play メソッドを呼び出す処理を行う
        そのため、仮引数 ai と ai_dict は play メソッドと同じ意味を持つ
              
        Args:
            ai: それぞれの手番を担当する AI の関数を要素として持つ list
                実引数を省略した場合は、人間どうしの対戦を行う
            ai_list:
                Dropdown で選択できる AI の項目を表す dict
                実引数を省略した場合は、ai1s ～ ai14s の項目を表す dict を作成する
            seed:
                最初のゲーム利用する乱数の種
    """

    # ai が None の場合は、人間どうしの対戦を行う
    if ai is None:
        ai = [None, None]
    # ai_dict が None の場合は、ai1s ~ ai14s の Dropdown を作成するためのデータを計算する
    if ai_dict is None:
        ai_dict = { "人間": "人間"}
        for i in range(1, 15):
            ai_name = f"ai{i}s"  
            ai_dict[ai_name] = getattr(ai_module, ai_name)
    
    mb = Marubatsu()
    mb.play(ai=ai, ai_dict=ai_dict, seed=seed, gui=True)
    
def load_bestmoves(fname:str="../data/bestmoves.dat"):
    """各局面の最善手の一覧を表すデータをファイルから読み込む

    Args:
        fname:
            データファイルのパス

    Returns:
        読み込んだデータ
    """

    with gzip.open(fname, "rb") as f:
        return pickle.load(f)
    
def load_mblist(fname:str="../data/mblist.dat"):
    """決着がついていない局面を表すデータをファイルから読み込む

    Args:
        fname:
            データファイルのパス

    Returns:
        読み込んだデータ
    """

    with gzip.open(fname, "rb") as f:
        return pickle.load(f)    
    
class Check_solved:
    """AI が解決されているかどうかを判定するクラス

    Attributes:
        クラス属性
        bestmoves_by_board(dict[str, list[tuple[int, int]]]):
            各局面の最善手の一覧を表すデータ
        mblist_by_board(list[Marubatsu]):
            決着がついていない局面を表す list
    """

    bestmoves_by_board = None
    mblist_by_board = None
    
    @staticmethod
    def is_strongly_solved(ai, params:dict|None=None) -> tuple[bool, list]:
        """強解決の AI であるかどうかを判定する.
        
        判定の処理の際に、最善手のみを選択する局面の数を表示する.
        
        Args:
            ai:
                判定する AI
            params:
                AI に渡すパラメータを表す dict
        
        Returns:
            以下の要素を持つ tuple を返す
                強解決の AI の場合は True、そうでない場合は False
                最善手を選択しない局面に関する下記の要素を持つ tuple
                    局面を表す Marubatsu クラスのインスタンス
                    その局面で AI が選択する着手の一覧
                    その局面での最善手の一覧
        """
        if Check_solved.bestmoves_by_board is None:
            Check_solved.bestmoves_by_board = load_bestmoves ("../data/bestmoves_by_board.dat")
        if Check_solved.mblist_by_board is None:
            Check_solved.mblist_by_board = load_mblist("../data/mblist_by_board_min.dat")            
        if params is None:
            params = {}
        count = 0
        incorrectlist = []
        for mb in tqdm(Check_solved.mblist_by_board):
            candidate = set(ai(mb, candidate=True, **params))
            bestmoves = set(Check_solved.bestmoves_by_board[mb.board_to_str()])
            if candidate <= bestmoves:
                count += 1
            else:
                incorrectlist.append((mb, candidate, bestmoves))
        nodenum = len(Check_solved.mblist_by_board)
        print(f"{count}/{nodenum} {count/nodenum*100:.2f}%")
        return count == nodenum, incorrectlist

def calc_same_boardtexts(mb:Marubatsu) -> set[str]:
    """同一の局面を表す文字列の一覧を計算する
    Args:
        mb:
            同一の局面を計算する局面を表す Marubatsu クラスのインスタンス

    Returns:
        同一の局面を表す文字列の一覧を表す set
    """

    data = [ [ 0,  0,  1, 1, -1,  0],
             [ 1, -1,  0, 1,  0, -1],
             [ 1,  0, -1, 0,  1,  0],
             [ 1, -1,  0, 0,  0,  1],
             [ 0,  1,  0, 1,  0, -1],
             [ 1,  0, -1, 1, -1,  0],
             [ 0,  0,  1, 0,  1,  0], ]
    boardtexts = set([mb.board_to_str()])
    for xa, xb, xc, ya, yb, yc in data:
        txt = ""
        for x in range(mb.BOARD_SIZE):
            for y in range(mb.BOARD_SIZE):
                txt += mb.board[xa * 2 + xb * x + xc * y][ya * 2 + yb * x + yc * y]
        boardtexts.add(txt)
    return boardtexts