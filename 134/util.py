from marubatsu import Marubatsu
from tree import Mbtree
import ai as ai_module
from ai import ai_gt6
import pickle
import gzip
from tqdm import tqdm

def gui_play(ai:list=None, params:list[dict]|None=None, ai_dict:dict[tuple]|None=None, seed:int|None=None):
    """GUI で 〇×ゲームを遊ぶ
    
        Marubatsu クラスのインスタンスを作成し、play メソッドを呼び出す処理を行う
        そのため、仮引数 ai と ai_dict は play メソッドと同じ意味を持つ
              
        Args:
            ai: それぞれの手番を担当する AI の関数を要素として持つ list
                実引数を省略した場合は、人間どうしの対戦を行う
            params:
                それぞれの手番を担当する AI の関数に渡すパラメータを要素として持つ list
                パラメータは dict で表現する
            ai_dict:
                Dropdown で選択できる AI の項目と AI のパラメータを表す dict
                実引数を省略した場合は、ai1s ～ ai14s の項目を表す dict を作成する
                dict のキーには Dropdown に表示する項目名を、キーの値には
                その AI の関数と関数に渡すパラメータを要素として持つ tuple を代入する
            seed:
                最初のゲーム利用する乱数の種
    """

    # ai が None の場合は、人間どうしの対戦を行う
    if ai is None:
        ai = [None, None]
    if params is None:
        params = [{}, {}]
    # ai_dict が None の場合は、ai1s ~ ai14s の Dropdown を作成するためのデータを計算する
    if ai_dict is None:
        ai_dict = { "人間": ( None, {} ) }
        for i in range(1, 15):
            ai_name = f"ai{i}s"  
            ai_dict[ai_name] = (getattr(ai_module, ai_name), {})
        bestmoves_by_board = load_bestmoves("../data/bestmoves_by_board.dat")
        ai_dict["ai_gt6"] = (ai_gt6, {"bestmoves_by_board": bestmoves_by_board})
        bestmoves_by_board_sv = load_bestmoves("../data/bestmoves_by_board_shortest_victory.dat")
        ai_dict["ai_gtsv"] = (ai_gt6, {"bestmoves_by_board": bestmoves_by_board_sv})

    mb = Marubatsu()
    mb.play(ai=ai, params=params, ai_dict=ai_dict, seed=seed, gui=True)
    
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
    mbtree = None
    mblist_by_board2 = None
    mblist_by_board_min = None
    
    @staticmethod
    def is_strongly_solved(ai, params:dict|None=None, consider_samedata:bool=True) -> tuple[bool, list]:
        """強解決の AI であるかどうかを判定する.
        
        判定の処理の際に、最善手のみを選択する局面の数を表示する.
        
        Args:
            ai:
                判定する AI
            params:
                AI に渡すパラメータを表す dict
            consider_samedata:
                True の場合に、同一局面を考慮した局面の一覧で判定する
        
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
        if consider_samedata:
            if Check_solved.mblist_by_board_min is None:
                Check_solved.mblist_by_board_min = load_mblist("../data/mblist_by_board_min.dat")
            mblist = Check_solved.mblist_by_board_min
        else:
            if Check_solved.mblist_by_board2 is None:
                Check_solved.mblist_by_board2 = load_mblist("../data/mblist_by_board2.dat") 
            mblist = Check_solved.mblist_by_board2        
        if params is None:
            params = {}
        count = 0
        incorrectlist = []
        for mb in tqdm(mblist):
            candidate = set(ai(mb, analyze=True, **params)["candidate"])
            bestmoves = set(Check_solved.bestmoves_by_board[mb.board_to_str()])
            if candidate <= bestmoves:
                count += 1
            else:
                incorrectlist.append((mb, candidate, bestmoves))
        nodenum = len(mblist)
        print(f"{count}/{nodenum} {count/nodenum*100:.2f}%")
        return count == nodenum, incorrectlist
    
    @staticmethod
    def is_weakly_solved(ai, params:dict|None=None, verbose:bool=True) -> bool:
        """弱解決の AI であるかどうかを判定する.
        
        Args:
            ai:
                判定する AI
            params:
                AI に渡すパラメータを表す dict
            verbose:
                True の場合に結果を表示する
        
        Returns:
            弱解決の AI の場合は True を、そうでない場合は False を返す
        """
        
        Check_solved.count = 0
        if params is None:
            params = {}
        if Check_solved.mbtree is None:
            Check_solved.mbtree = Mbtree.load("../data/aidata")
        root = Check_solved.mbtree.root
        circle_result = Check_solved.is_weakly_solved_r(root, ai, Marubatsu.CIRCLE, params, set())
        cross_result = Check_solved.is_weakly_solved_r(root, ai, Marubatsu.CROSS, params, set())
        result = circle_result and cross_result
        if verbose:
            print("   o", circle_result)
            print("   x", cross_result)
            print("Both", result)
        return result    
    
    @staticmethod
    def is_weakly_solved_r(node, ai, turn:str, params:dict, registered_boards:set) -> bool:
        """弱解決の AI であるかどうかを判定する際に利用する再起呼び出しのメソッド
        
        Args:
            node:
                判定を行うノード
            ai:
                判定する AI
            turn:
                判定する AI の手番
            params:
                AI に渡すパラメータを表す dict
            registered_boards:
                判定済のノードを表す set
        
        Returns:
            弱解決の AI の場合は True を、そうでない場合は False を返す
        """
        
        txt = node.mb.board_to_str()
        if txt in registered_boards:
            return True
        Check_solved.count += 1
        registered_boards.add(txt)
        if node.mb.status == turn or node.mb.status == Marubatsu.DRAW:
            return True
        elif node.mb.status != Marubatsu.PLAYING:
            return False
            
        if turn == node.mb.turn:
            moves = ai(node.mb, analyze=True, **params)["candidate"]
        else:
            moves = node.mb.calc_legal_moves()
        for move in moves:
            childnode = node.children_by_move[move]
            if not Check_solved.is_weakly_solved_r(childnode, ai, turn, params, registered_boards):
                return False
        return True 

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
