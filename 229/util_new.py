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
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

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

def create_pd(minx:int, maxx:int):
    """整数を確率変数の値とする離散型確率分布を作成する.

    確率変数が minx 以上 maxx 以下の整数の値をとる確率分布を作成する
    それぞれの確率変数の確率は一様乱数で計算する

    Args:
        minx (int): 確率変数の最小値
        maxx (int): 確率変数の最大値

    Returns:
        確率変数の値の一覧を表す 1 次元の ndarray と
        対応する確率の一覧を表す 1 次元の ndarray を要素として持つ tuple
    """
        
    xnum = maxx - minx + 1
    X = np.arange(minx, maxx + 1)
    P = np.random.uniform(size=xnum)
    P /= np.sum(P)
    return X, P

def calc_abs_pd(X, P):
    """確率変数の絶対値で定義される確率分布を計算する

    Args:
        X: 確率変数の値の一覧を表す 1 次元の ndarray
        P: 対応する確率の一覧を表す 1 次元の ndarray

    Returns:
        計算した確率変数の値の一覧を表す 1 次元の ndarray と
        対応する確率の一覧を表す 1 次元の ndarray を要素として持つ tuple
    """
    
    maxx = max(max(X), max(-X))
    Xabs = np.arange(0, maxx + 1)
    Pabs = np.zeros_like(Xabs, dtype=np.float32)
    for x, p in zip(X, P):
        Pabs[abs(x)] += p
    return Xabs, Pabs


def check_markov(X, P, maxa:int):
    """ 1 以上 maxa 以下の a の値に対してマルコフの不等式が成り立つかどうかを計算する

    Args:
        X: 確率変数の値の一覧を表す 1 次元の ndarray
        P: 対応する確率の一覧を表す 1 次元の ndarray
        maxa (int): a の最大値
    """
    
    Xabs, Pabs = calc_abs_pd(X, P)
    Eabs = np.sum(Xabs * Pabs)
    Vabs = np.sum(Xabs * Xabs * Pabs) - Eabs ** 2
    print(f"E[|X|] = {Eabs:6.3f}")
    print(f"V[|X|] = {Vabs:6.3f}")
    for a in range(1, maxa + 1):
        Pgta = np.ma.array(Pabs, mask=Xabs<a)
        p = np.sum(Pgta)
        print(f"P(|X| ≧ {a:2d}) = {p:.3f} E[|X|]/{a:2d} = {Eabs/a:4.3f} {p <= Eabs/a}")
        
def show_pd(X, P, xlabel:str="X", cond=None, labelt:str="", labelf:str=""):
    """確率分布の期待値と分散を表示し、確率分布のグラフを描画する
    
    cond が None 出ない場合は cond の条件を満たす確率変数の範囲と、満たさない場合で
    描画するグラフの色を変える

    Args:
        X: 確率変数の値の一覧を表す 1 次元の ndarray
        P: 対応する確率の一覧を表す 1 次元の ndarray
        xlabel (str, optional): グラフの x 軸に表示するラベル
        cond (optional): グラフの色を変化させる確率変数の範囲を表す 1 次元の ndarray
                         None の場合は色分けをしない
        labelt (str, optional): cond が True の範囲のグラフの凡例に表示するラベル
        labelf (str, optional): cond が False の範囲のグラフの凡例に表示するラベル
    """
    E = np.sum(X * P)
    V = np.sum(X * X * P) - E ** 2
    print(f"期待値 = {E:6.3f}")
    print(f"分散   = {V:6.3f}")
    if cond is None:
        plt.bar(X, P)
    else:
        Pfalse = np.ma.array(P, mask=cond)
        Ptrue = np.ma.array(P, mask=~cond)
        plt.bar(X, Pfalse, label=labelf)
        plt.bar(X, Ptrue, label=labelt)
        plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel("確率")
    plt.show()
        
def check_chebyshev(X, P, maxa):
    """ 1 以上 maxa 以下の a の値に対してチェビシェフの不等式が成り立つかどうかを計算する

    Args:
        X: 確率変数の値の一覧を表す 1 次元の ndarray
        P: 対応する確率の一覧を表す 1 次元の ndarray
        maxa (int): a の最大値
    """
    
    E = np.sum(X * P)
    V = np.sum(X * X * P) - E ** 2
    print(f"E[X] = {E:6.3f}")
    print(f"V[X] = {V:6.3f}")
    for a in range(1, maxa + 1):
        Pgta = np.ma.array(P, mask=np.abs(X - E)<a)
        p = np.sum(Pgta)
        print(f"P(|X - E[X]| ≧ {a:2d}) = {p:.3f}  V[X]/{(a ** 2):3d} = {V/(a ** 2):6.3f} {p <= V/a/a}")