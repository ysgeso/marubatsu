from marubatsu import Marubatsu
from tree import Mbtree
import ai as ai_module
from ai import ai_gt7
import timeit
import pickle
import gzip
import random
from tqdm import tqdm
from statistics import mean, stdev

def gui_play(ai:list=None, params:list[dict]|None=None, ai_dict:dict[tuple]|None=None, mbparams:dict={}, seed:int|None=None):
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
            mbparams:
                Marubatsu クラスのインスタンスを作成する際に記述する実引数を表す dict
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
        bestmoves_and_score_by_board = load_bestmoves("../data/bestmoves_and_score_by_board.dat")
        ai_dict["ai_gt7"] = (ai_gt7, {"bestmoves_and_score_by_board": bestmoves_and_score_by_board})
        bestmoves_and_score_by_board_sv = load_bestmoves("../data/bestmoves_and_score_by_board_shortest_victory.dat")
        ai_dict["ai_gtsv"] = (ai_gt7, {"bestmoves_and_score_by_board": bestmoves_and_score_by_board_sv})
        bestmoves_and_score_by_board_svrd = load_bestmoves("../data/bestmoves_and_score_by_board_sv_rd.dat")
        ai_dict["ai_gtsvrd"] = (ai_gt7, {"bestmoves_and_score_by_board": bestmoves_and_score_by_board_svrd})

    mb = Marubatsu(**mbparams)
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
        circle_result = Check_solved.is_weakly_solved_r(root, ai, root.mb.CIRCLE, params, set())
        cross_result = Check_solved.is_weakly_solved_r(root, ai, root.mb.CROSS, params, set())
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
        if node.mb.status == turn or node.mb.status == node.mb.DRAW:
            return True
        elif node.mb.status != node.mb.PLAYING:
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

def calc_same_boardtexts(mb:Marubatsu, move:tuple[int, int]|None=None) -> set[str]|dict:
    """同一の局面を表す文字列と、move に対応する同一局面の合法手の一覧を計算する
    
    Args:
        mb:
            同一の局面を計算する局面を表す Marubatsu クラスのインスタンス
        move:
            合法手を表すデータ。None の場合は同一局面を表す文字列のみを計算する

    Returns:
        move が None の場合は同一の局面を表す文字列の一覧を表す set
        そうでない場合は、同一局面を表す文字列をキーとし、 move に対応する同一局面の合法手をキーの値とする dict
    """

    data = [ [ 0,  0,  1, 1, -1,  0,  1,  0, -1, 0,  1,  0],
             [ 1, -1,  0, 1,  0, -1] * 2,
             [ 1,  0, -1, 0,  1,  0,  0,  0,  1, 1, -1,  0],
             [ 1, -1,  0, 0,  0,  1] * 2,
             [ 0,  1,  0, 1,  0, -1] * 2,
             [ 1,  0, -1, 1, -1,  0] * 2,
             [ 0,  0,  1, 0,  1,  0] * 2, ]
    if move is None:
        boardtexts = set([mb.board_to_str()])
    else:
        boardtexts = { mb.board_to_str(): move }
    for xa, xb, xc, ya, yb, yc, xa2, xb2, xc2, ya2, yb2, yc2 in data:
        txt = ""
        for x in range(mb.BOARD_SIZE):
            for y in range(mb.BOARD_SIZE):
                txt += mb.board.getmark(xa * (mb.board.BOARD_SIZE -1) + xb * x + xc * y, 
                                        ya * (mb.board.BOARD_SIZE -1) + yb * x + yc * y)
        if move is None:
            boardtexts.add(txt)
        else:
            x, y = mb.board.move_to_xy(move)
            x, y = xa2 * (mb.board.BOARD_SIZE -1) + xb2 * x + xc2 * y, ya2 * (mb.board.BOARD_SIZE -1) + yb2 * x + yc2 * y
            boardtexts[txt] = mb.board.xy_to_move(x, y)
    return boardtexts

def benchmark(mbparams:dict={}, match_num:int=50000, seed:int|None=0, number:int=10, repeat:int=7):
    """3 種類のベンチマークを実行する
    
    ベンチマークは下記の 3 種類
    ai2 VS ai2
    ai14s VS ai2
    ai_abs_dls
    
    Args:
        mbparams:
            Marubatsu クラスのインスタンスを作成する際に記述する実引数を表す dict
        match_num:
            ai_match で対戦を行う回数
        seed:
            乱数の種。None が代入されている場合は乱数の種を初期化しない
        number:
            timeit.repeat の仮引数 number に代入する値
        repeat:
            timeit.repeat の仮引数 repeat に代入する値
    """

    if seed is not None:
        random.seed(seed)       
        
    from ai import ai2, ai14s, ai_match, ai_abs_dls

    ai_match(ai=[ai2, ai2], match_num=match_num, mbparams=mbparams)   
    ai_match(ai=[ai14s, ai2], match_num=match_num, mbparams=mbparams)

    mb = Marubatsu(**mbparams)
    eval_params = {"minimax": True}
    stmt = "ai_abs_dls(mb, eval_func=ai14s, eval_params=eval_params, use_tt=True, maxdepth=8)"
    print("ai_abs_dls")
    result = timeit.repeat(stmt=stmt, number=number, repeat=repeat, globals=locals())
    result = [time / number for time in result]
    print(f"{mean(result) * 1000:5.1f} ms ± {stdev(result) * 1000:5.1f} ms per loop (mean ± std. dev. of {repeat} runs, {number} loops each)")
