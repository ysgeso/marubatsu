from marubatsu import Marubatsu
from tree import Mbtree
import ai as ai_module
from ai import ai_gt7, ai_pmc
import timeit
import pickle
import gzip
import random
from tqdm import tqdm
from statistics import mean, stdev
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
from statistics import NormalDist
from copy import deepcopy
from time import perf_counter

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
        for pnum in [5, 10, 100, 1000, 10000]:
            ai_dict[f"ai_pmc({pnum})"] = (ai_pmc, {"pnum": pnum})
            
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
        
def sampling(X, P, size:int):
    """無作為復元抽出の結果をグラフで描画し各要素の個数を返す

    Args:
        X: 確率変数の値の一覧を表す 1 次元の ndarray
        P: 対応する確率の一覧を表す 1 次元の ndarray
        size (int): 抽出する標本の個数

    Returns:
        下記の 1 次元の ndarray を要素とする tuple
            抽出した要素の一覧
            各要素の個数を表す
    """
    result = {e: 0 for e in X}
    sizeleft = size
    while sizeleft > 0:
        s = min(sizeleft, 1000000)
        sample = np.random.choice(X, p=P, size=s)    
        element, count = np.unique(sample, return_counts=True) 
        for e, c in zip(element, count):
            result[e] += c
        sizeleft -= s
    element = np.array(list(result.keys()))
    count = np.array(list(result.values()))
      
    plt.figure(figsize=(4, 3))
    width = 0.4
    plt.bar(element - width / 2, count / size, width=width, label="x の割合")
    plt.bar(X + width / 2 , P, width=width, label="P(X=x)")
    plt.xlabel("x")
    plt.ylabel("割合・確率")
    plt.ylim(0, max(count/size) + 0.07)
    plt.title(f"size = {size}")
    plt.legend()
    plt.show()
    return element, count   

def sampling_and_analyze(X, P, size:int, num:int, bins:int=None, maxe:int=1000000):
    """無作為復元抽出によって複数個の標本抽出を行い分析を行う

    行う処理は以下の通り
    X、P が表す確率変数の母平均と母分散を計算する
    X、P が表す確率分布から 標本サイズが size の標本を num 個無作為復元抽出する
    各標本の標本平均を計算し、標本平均の分散を計算する
    標本平均のヒストグラムと中心極限定理から計算される標本平均を近似する正規分布のグラフを描画する

    Args:
        X: 確率変数の値の一覧を表す 1 次元の ndarray
        P: 対応する確率の一覧を表す 1 次元の ndarray
        size (int): 抽出する標本の標本サイズ
        num (int): 抽出する標本数
        bins (int): ヒストグラムのビンの数。None の場合は自動で計算する
        maxe: 一度で抽出する標本の要素の最大数
    """
    
    print(f"標本サイズ = {size}")
    E = np.average(X, weights=P)
    V = np.average(X ** 2, weights=P) - E ** 2
    print(f"母平均           = {E:.7f}")
    print(f"母分散           = {V:.7f}")

    numleft = num
    maxs = min(size, maxe)
    maxn = min(num, maxe // maxs)
    mean = []
    while numleft > 0:
        sizeleft = size
        n = min(numleft, maxn)
        total = np.zeros(n)
        while sizeleft > 0:
            s = min(sizeleft, maxe)
            sample = np.random.choice(X, p=P, size=(s, n)) 
            total += np.sum(sample, axis=0)  
            sizeleft -= s
        mean += (total / size).tolist()
        numleft -= n
    var = np.var(mean)
    print(f"標本平均の分散    = {var:.7f}") 
    print(f"母分散÷標本サイズ = {V/size:.7f}") 
    print(f"誤差             = {np.abs(var - V/size):.7f}") 
    
    if bins is None:
        element = np.unique(mean)
        bins = max(len(X), min(int(np.sqrt(len(element))) * 2, 50))
    plt.hist(mean, bins=bins, density=True)
    ndist = NormalDist(E, np.sqrt(V/size))
    NX = np.linspace(min(mean), max(mean), 100)
    NY = [ndist.pdf(x) for x in NX]
    plt.plot(NX, NY)
    plt.title(f"標本サイズ {size}")
    plt.show()

def playout(mborig, pnum:int, timelimit:float|None=None) -> dict:
    """指定した回数のプレイアウトを行いその結果を返す

    Args:
        mborig (_type_): プレイアウトを行う局面
        pnum (int): プレイアウトを行う回数
        timelimit (float | None, optional): 制限時間（単位は秒）。None の場合は制限時間を設けない

    Returns:
        下記の dict
        {
            "result": {
                最初の着手を表すデータ: {
                    mb.CIRCLE: 〇 の勝利の回数,
                    mb.CROSS: × の勝利の回数,
                    mb.DRAW: 引き分けの回数,
                }
            },
            "count": プレイアウトを行った回数
        }
    """
    
    if timelimit is not None:   
        starttime = perf_counter()
        timelimit_pc = starttime + timelimit        
    result = {}
    for move in mborig.calc_legal_moves():
        result[move] = {
            mborig.CIRCLE: 0,
            mborig.CROSS: 0,
            mborig.DRAW: 0,
        }
    count = 0
    for _ in range(pnum):
        if timelimit is not None and perf_counter() > timelimit_pc:
            break
        mb = deepcopy(mborig)
        firstmove = None
        while mb.status == mb.PLAYING:
            move = random.choice(mb.calc_legal_moves())
            if firstmove is None:
                firstmove = move
            mb.move(move)
        result[firstmove][mb.status] += 1
        count += 1
    return {
        "result": result,
        "count": count,
    }
    
def analyze_playout(mb, retval, mbtree):
    """playout の結果を分析して表示する.

    Args:
        mb (_type_): playout でプレイアウトを行った局面
        retval (_type_): playout の返り値
        mbtree (_type_): 各ノードにプレイアウトの確率（playout_prob 続映）が計算された Mbtree のインスタンス
    """
    
    print(f"playout count = {retval['count']}")
    diffsum = 0
    diffcount = 0
    for move, counts in retval["result"].items():
        print(f"move {mb.board.move_to_xy(move)}")
        mb.move(move)
        print(mb)
        node = mbtree.nodelist_by_mb[tuple(mb.records)]
        mb.unmove()
        total = max(1, sum(counts.values()))
        print("        count   ratio    prob    diff")
        for status, count in counts.items():
            mark = mb.board.MARK_TABLE[status]
            ratio = count / total * 100
            prob = node.playout_prob[status] * 100
            diff = abs(ratio - prob)
            diffsum += diff
            diffcount += 1
            print(f"{mark:4s}: {count:7d} {ratio:6.2f}% {prob:6.2f}% {diff:6.2f}%")
        print()
        print("-------------------------------------")
        print()
    print(f"diff average = {diffsum / diffcount:6.2f}%")
    print()