# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from marubatsu import Marubatsu, Markpat
from random import choice
from collections import defaultdict
from copy import deepcopy
from pprint import pprint
from tree import Mbtree
from tqdm import tqdm
from functools import wraps

def dprint(debug:bool, *args, **kwargs):
    """デバッグ表示を行う.
    
    debug が True の場合に、2 つ目以降の実引数を print で表示する
    
    Args:
        debug:
            True の場合にデバッグ表示を行う
            False の場合は何も表示しない
    
    """
    
    if debug:
        print(*args, **kwargs)

def ai_match(ai:list, params:list[dict]=[{}, {}], match_num:int=10000):
    """AIどうしの対戦を行い、通算成績を表示する

    Args:
        ai:
            それぞれの手番を担当する AI の関数を指定する list
            0 番の要素が 〇 の手番、1 番の要素が × の手番を表す
            AI の処理を行う関数の仮引数は Marubatsu クラスのインスタンスで、
            着手を行う座標を表す (x, y) の形式の tuple を返すものとする
        params:
            それぞれの AI に渡すパラメータを要素として持つ list
            パラメータは、マッピング型の展開で AI に渡す
        match_num:
            対戦を行う回数
    """

    print(f"{ai[0].__name__} VS {ai[1].__name__}")
    
    mb = Marubatsu()

    # ai[0] VS ai[1] と ai[1] VS a[0] の対戦を match_num 回行い、通算成績を数える
    count_list = [ defaultdict(int), defaultdict(int)]
    for _ in tqdm(range(match_num)):
        count_list[0][mb.play(ai, params=params, verbose=False)] += 1
        count_list[1][mb.play(ai=ai[::-1], params=params[::-1], verbose=False)] += 1

    # ai[0] から見た通算成績を計算する
    count_list_ai0 = [
        # ai[0] VS ai[1] の場合の、ai[0] から見た通算成績
        { 
            "win": count_list[0][Marubatsu.CIRCLE],
            "lose": count_list[0][Marubatsu.CROSS],
            "draw": count_list[0][Marubatsu.DRAW],
        },
        # ai[1] VS ai[0] の場合の、ai[0] から見た通算成績
        { 
            "win": count_list[1][Marubatsu.CROSS],
            "lose": count_list[1][Marubatsu.CIRCLE],
            "draw": count_list[1][Marubatsu.DRAW],
        },
    ]           

    # 両方の対戦の通算成績の合計を計算する
    count_list_ai0.append({})
    for key in count_list_ai0[0]:
        count_list_ai0[2][key] = count_list_ai0[0][key] + count_list_ai0[1][key]

    # それぞれの比率を計算し、ratio_list に代入する
    ratio_list = [ {}, {}, {} ]
    for i in range(3):
        for key in count_list_ai0[i]:
            ratio_list[i][key] = count_list_ai0[i][key] / sum(count_list_ai0[i].values())
            
    # 各行の先頭に表示する文字列のリスト
    item_text_list = [ Marubatsu.CIRCLE, Marubatsu.CROSS, "total" ]    
    
    # 通算成績の回数と比率の表示
    width = max(len(str(match_num * 2)), 7)
    diff_list = [ ("count", count_list_ai0, f"{width}d"),
                  ("ratio", ratio_list, f"{width}.1%") ]
    for title, data, format in diff_list:
        print(title, end="")
        for key in data[0]:
            print(f" {key:>{width}}", end="")
        print()
        for i in range(3):
            print(f"{item_text_list[i]:5}", end="")
            for value in data[i].values():
                print(f" {value:{format}}", end="")
            print()
        print()

def ai_by_score(eval_func):
    """評価値を利用した AI のラッパー関数を作成するデコレーター
    
    Args:
        eval_func:
            以下の仮引数と返り値を持つ評価関数
            仮引数: 
                mb:
                    評価値を計算する局面を表す Marubatsu クラスのインスタンス
                debug:
                    True の場合にデバッグ表示を行う
                パラメータ(必要なだけ):
                    評価値を計算するために必要なパラメーター
                
                返り値:
                    計算した評価値
            
    Returns:
        下記の wrapper で定義したラッパー関数
    """
    
    @wraps(eval_func)
    def wrapper(mb_orig:Marubatsu, debug:bool=False, *args, rand:bool=True, analyze:bool=False, **kwargs):
        """評価値を利用した AI のラッパー関数型.

        mb_orig の局面に対して、eval_func の評価関数を使って、評価値を利用した
        アルゴリズムで着手を選択する

        Args:
            mb_orig: 
                現在の局面を表す Marubatsu クラスのインスタンス
            debug:
                True の場合にデバッグ表示を行う
            rand:
                True の場合は、最善手の中からランダムで着手を選択する
                False の場合は、先頭の最善手の着手を選択する
            analyze:
                False の場合に、着手する座標を表す tuple を返す
                True の場合に、候補手の一覧と、それぞれの合法手に着手した場合の評価値を
                表す下記の dict を返す
                    candidate: 
                        候補手の一覧を表す list
                    score_by_move: 
                        合法手をキーとし、そのキーの値に合法手を着手した場合の
                        評価値を代入した dict
            *args:
            **kwargs:
                評価関数にそのまま渡す仮引数

        Returns:
            着手する座標を表す tuple または、
            候補手の一覧と、それぞれの合法手に着手した場合の評価値を表す dict
        """    

        dprint(debug, "Start ai_by_score")
        dprint(debug, mb_orig)
        legal_moves = mb_orig.calc_legal_moves()
        dprint(debug, "legal_moves", legal_moves)
        best_score = float("-inf")
        best_moves = []
        if analyze:
            score_by_move = {}
        for move in legal_moves:
            dprint(debug, "=" * 20)
            dprint(debug, "move", move)
            mb = deepcopy(mb_orig)
            x, y = move
            mb.move(x, y)
            dprint(debug, mb)
            
            score = eval_func(mb, debug, *args, **kwargs)
            dprint(debug, "score", score, "best score", best_score)
            if analyze:
                score_by_move[move] = score
            
            if best_score < score:
                best_score = score
                best_moves = [move]
                dprint(debug, "UPDATE")
                dprint(debug, "  best score", best_score)
                dprint(debug, "  best moves", best_moves)
            elif best_score == score:
                best_moves.append(move)
                dprint(debug, "APPEND")
                dprint(debug, "  best moves", best_moves)

        dprint(debug, "=" * 20)
        dprint(debug, "Finished")
        dprint(debug, "best score", best_score)
        dprint(debug, "best moves", best_moves)
        if analyze:
            return {
                "candidate": best_moves,
                "score_by_move": score_by_move,
            }
        elif rand:   
            return choice(best_moves)
        else:
            return best_moves[0]
        
    return wrapper

def ai_by_candidate(func):
    """評価値を利用しない AI のラッパー関数を作成するデコレーター
    
    Args:
        eval_func:
            以下の仮引数と返り値を持つ評価関数
            仮引数: 
                mb:
                    候補手の一覧を計算する局面を表す Marubatsu クラスのインスタンス
                debug:
                    True の場合にデバッグ表示を行う
                パラメータ(必要なだけ):
                    候補手の一覧を計算するために必要なパラメーター
                
                返り値:
                    候補手の一覧を表すデータ
            
    Returns:
        下記の wrapper で定義したラッパー関数
    """
        
    @wraps(func)
    def wrapper(mb:Marubatsu, debug:bool=False, *args, rand:bool=True, analyze:bool=False, **kwargs):
        """評価値を利用しない AI のラッパー関数型.

        mb の局面に対して、func を使って、候補手の一覧を計算し、
        それに対して仮引数 debug、rand、analyze の値に応じた処理を行う

        Args:
            mb: 
                現在の局面を表す Marubatsu クラスのインスタンス
            debug:
                True の場合にデバッグ表示を行う
            rand:
                True の場合は、最善手の中からランダムで着手を選択する
                False の場合は、先頭の最善手の着手を選択する
            analyze:
                False の場合に、着手する座標を表す tuple を返す
                True の場合に、候補手の一覧と、それぞれの合法手に着手した場合の評価値を
                表す下記の dict を返す。ただし、評価値は計算しないので、score_by_move の値は None とする
                    candidate: 
                        候補手の一覧を表す list
                    score_by_move: 
                        None
            *args:
            **kwargs:
                評価関数にそのまま渡す仮引数

        Returns:
            着手する座標を表す tuple または、
            候補手の一覧と、それぞれの合法手に着手した場合の評価値を表す dict
        """    
        
        candidate = func(mb, debug, *args, **kwargs)
        dprint(debug, "candidate", candidate)
        if analyze:
            return {
                "candidate": candidate,
                "score_by_move": None
            }
        else:
            if rand:
                return choice(candidate)
            else:
                return candidate[0]
        
    return wrapper

def show_progress(ai:list, winner:str, params=[{}, {}]):
    """指定した AIどうしの、指定した結果の対戦経過を表示する.

    ai で指定した AI どうしで、winner で指定した対戦結果が生じるまで
    対戦を行い、その対戦の経過を表示する
    winner で指定した対戦結果が生じないような AI どうしで対戦を行うと
    無限ループが発生する点に注意すること

    Args:
        ai:
            それぞれの手番を担当する AI の関数を指定する list
            0 番の要素が 〇 の手番、1 番の要素が × の手番を表す
            AI の処理を行う関数の仮引数は Marubatsu クラスのインスタンスで、
            着手を行う座標を表す (x, y) の形式の tuple を返すものとする
        winner:
            表示する対戦結果を表す文字列
        params:
            それぞれの AI に渡すパラメータを要素として持つ list
            パラメータは、マッピング型の展開で AI に渡す
    """
    
    mb = Marubatsu()
    while True:
        if mb.play(ai=ai, verbose=False, params=params) == winner:
            records = mb.records
            mb.restart()
            for x, y in records:
                mb.move(x, y)
                print(mb)
            break

@ai_by_candidate
def ai1(mb:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """左上から順に空いているマスを探し、最初に見つかったマスに着手する AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う        

    Returns:
        候補手の一覧を表す list
    """

    for y in range(mb.BOARD_SIZE):
        for x in range(mb.BOARD_SIZE):
            if mb.board[x][y] == Marubatsu.EMPTY:
                return [(x, y)]

@ai_by_score
def ai1s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、左上から順に空いているマスを探し、最初に見つかったマスに着手する AI.

    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """
    
    if mb.last_move is None:
        return 0
    else:
        x, y = mb.last_move
        return 8 - (x + y * 3)

@ai_by_candidate
def ai2(mb:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """ランダムなマスに着手する AI.
    
    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        候補手の一覧を表す list
    """
    
    legal_moves = mb.calc_legal_moves()
    return legal_moves

@ai_by_score
def ai2s(mb:Marubatsu, debug:bool=False) -> float:
    """ランダムなマスに着手する AI の評価関数
    
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """
    
    return 0

@ai_by_candidate
def ai3(mb:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """真ん中のマスに優先的に着手する AI.

    以下のルールで着手を行う
    1. 真ん中のマスが空いていれば、そこに着手する
    2. 真ん中のマスが空いていなければ、ランダムなマスに着手する
    
    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        候補手の一覧を表す list
    """
    
    if mb.board[1][1] == Marubatsu.EMPTY:
        candidate = [(1, 1)]
    else:
        candidate = mb.calc_legal_moves()
    return candidate

@ai_by_score
def ai3s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、真ん中のマスに優先的に着手する AI.

    以下のルールで着手を行う
    1. 真ん中のマスが空いていれば、そこに着手する
    2. 真ん中のマスが空いていなければ、ランダムなマスに着手する
    
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """   
    
    if mb.last_move == (1, 1):
        return 1
    else:
        return 0

@ai_by_candidate
def ai4(mb:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """真ん中、隅のマスの順に優先的に着手する AI.

    以下のルールで着手を行う
    1. 真ん中のマスが空いていれば、そこに着手 する
    2. 真ん中のマスが空いていなければ、次に四隅のマスを左上から順に調べ、最初に見つかった、空いているマスに着手 する
    3. 四隅も空いていなければ、ランダムなマスに着手 する
    
    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う

    Returns:
        候補手の一覧を表す list
    """ 
    
    if mb.board[1][1] == Marubatsu.EMPTY:
        return [(1, 1)]
    for y in range(0, 3, 2):
        for x in range(0, 3, 2):
            if mb.board[x][y] == Marubatsu.EMPTY:
                return [(x, y)]
    return mb.calc_legal_moves()

@ai_by_score
def ai4s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、真ん中、隅のマスの順に優先的に着手する AI.

    以下のルールで着手を行う
    1. 真ん中のマスが空いていれば、そこに着手 する
    2. 真ん中のマスが空いていなければ、次に四隅のマスを左上から順に調べ、最初に見つかった、空いているマスに着手 する
    3. 四隅も空いていなければ、ランダムなマスに着手 する
    
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """     
    
    x, y = mb.last_move
    if mb.last_move == (1, 1):
        return 10
    elif x % 2 == 0 and y % 2 == 0:
        return 9 - (x + y * 3)
    else:
        return 0

@ai_by_candidate
def ai5(mb_orig:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """勝てるときに勝つ AI.

    以下のルールで着手を行う
    1. 合法手の中で、勝てるマスがあれば、そのマスに着手する
    2. 勝てるマスがなければランダムなマスに着手する
    
    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う

    Returns:
        候補手の一覧を表す list
    """
    
    legal_moves = mb_orig.calc_legal_moves()
    # すべての合法手について繰り返し処理を行う
    for move in legal_moves:
        # mb_orig をコピーし、コピーしたもの対して着手を行う
        mb = deepcopy(mb_orig)
        x, y = move
        mb.move(x, y)
        # 勝利していれば、その合法手を返り値として返す
        if mb.status == mb_orig.turn:
            return [move]
    return legal_moves

@ai_by_score
def ai5s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、勝てるときに勝つ AI.

    以下のルールで着手を行う
    1. 合法手の中で、勝てるマスがあれば、そのマスに着手する
    2. 勝てるマスがなければランダムなマスに着手する
    
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """  
    
    if mb.status == mb.last_turn:
        return 1
    else:
        return 0

@ai_by_candidate
def ai6(mb_orig:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """勝てるときに勝ち、相手の勝利を阻止する AI.

    以下のルールで着手を行う
    1. 合法手の中で、勝てるマスがあれば、そのマスに着手する
    2. そうでなければ、合法手 を 着手 した 局面 のうち、次 の 相手の手番 で、
       相手が着手 すると 相手が勝利 するマスが 存在すれば 、そこに着手 して 邪魔 をする
    3. 上記のいずれでもなければ ランダム なマスに 着手 する
    
    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う

    Returns:
        候補手の一覧を表す list
    """ 
    
    # mb_orig の合法手の中で、自分が勝利できる合法手があればそこに着手する
    legal_moves = mb_orig.calc_legal_moves()
    # 合法手が 1 つしかない場合は、その合法手を返り値として返す
    if len(legal_moves) == 1:
        return legal_moves
    # 合法手の中で、勝てるマスがあれば、その合法手を返り値として返す
    for move in legal_moves:
        mb = deepcopy(mb_orig)
        x, y = move
        mb.move(x, y)
        if mb.status == mb_orig.turn:
            return [move]
    # 〇 が勝利する合法手が存在しないことが確定した場合は、
    # 現在の局面を相手の手番とみなし、合法手の中で、相手が着手して
    # 勝利するマスがあれば、その合法手を返り値として返す
    for move in legal_moves:
        mb = deepcopy(mb_orig)
        # 現在の局面の手番を入れ替える
        mb.turn = Marubatsu.CROSS if mb.turn == Marubatsu.CIRCLE else Marubatsu.CIRCLE
        enemy_turn = mb.turn
        x, y = move
        mb.move(x, y)
        if mb.status == enemy_turn:
            return [move]
       
    return legal_moves

@ai_by_score
def ai6s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、勝てるときに勝ち、相手の勝利を阻止する AI.

    以下のルールで着手を行う
    1. 合法手の中で、勝てるマスがあれば、そのマスに着手する
    2. そうでなければ、合法手 を 着手 した 局面 のうち、次 の 相手の手番 で、
       相手が着手 すると 相手が勝利 するマスが 存在すれば 、そこに着手 して 邪魔 をする
    3. 上記のいずれでもなければ ランダム なマスに 着手 する
    
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """   
    
    # 自分が勝利している場合は、評価値として 1 を返す
    if mb.status == mb.last_turn:
        return 1

    # 相手の手番で相手が勝利できる場合は評価値として -1 を返す
    # 横方向と縦方向の判定
    for i in range(mb.BOARD_SIZE):
        count = mb.count_marks(coord=[0, i], dx=1, dy=0)
        if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
            return -1
        count = mb.count_marks(coord=[i, 0], dx=0, dy=1)
        if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
            return -1
    # 左上から右下方向の判定
    count = mb.count_marks(coord=[0, 0], dx=1, dy=1)
    if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
        return -1
    # 右上から左下方向の判定
    count = mb.count_marks(coord=[2, 0], dx=-1, dy=1)
    if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
        return -1

    # それ以外の場合は評価値として 0 を返す
    return 0

@ai_by_candidate
def ai7(mb:Marubatsu, debug:bool=False) -> list[tuple[int, int]]:
    """ai3 と ai6 を組み合わせた AI.

    以下のルールで着手を行う
    1. 真ん中のマスに優先的に着手する（ai3）
    2. そうでなければ、ai6 を使って着手を選択する
    
    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う

    Returns:
        候補手の一覧を表す list
    """    
    
    if mb.board[1][1] == Marubatsu.EMPTY:
        return [(1, 1)]
    return ai6(mb, debug=debug, analyze=True)["candidate"]

@ai_by_score
def ai7s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、ai3 と ai6 を組み合わせた AI.

    以下のルールで着手を行う
    1. 真ん中のマスに優先的に着手する（ai3）
    2. そうでなければ、ai6 を使って着手を選択する
    
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """  

    # 真ん中のマスに着手している場合は、評価値として 2 を返す
    if mb.last_move == (1, 1):
        return 2

    # 自分が勝利している場合は、評価値として 1 を返す
    if mb.status == mb.last_turn:
        return 1

    # 相手の手番で相手が勝利できる場合は評価値として -1 を返す
    # 横方向と縦方向の判定
    for i in range(mb.BOARD_SIZE):
        count = mb.count_marks(coord=[0, i], dx=1, dy=0)
        if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
            return -1
        count = mb.count_marks(coord=[i, 0], dx=0, dy=1)
        if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
            return -1
    # 左上から右下方向の判定
    count = mb.count_marks(coord=[0, 0], dx=1, dy=1)
    if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
        return -1
    # 右上から左下方向の判定
    count = mb.count_marks(coord=[2, 0], dx=-1, dy=1)
    if count[mb.turn] == 2 and count[Marubatsu.EMPTY] == 1:
        return -1

    # それ以外の場合は評価値として 0 を返す
    return 0

@ai_by_score
def ai8s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、以下のルールで着手を行う AI.

    以下のルールで着手を行う
    1. 真ん中のマスに優先的に着手する
    2. そうでない場合は、勝てる場合に勝つ
    3. そうでない場合は、相手が勝利できる着手を行わない
    4. そうでない場合は、次の自分の手番で勝利できるように、
       「自 2 敵 0 空 1」が 1 つ以上存在する局面になる着手を行う
    5. そうでない場合はランダムなマスに着手する    
  
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """     

    # 真ん中のマスに着手している場合は、評価値として 3 を返す
    if mb.last_move == (1, 1):
        return 3

    # 自分が勝利している場合は、評価値として 2 を返す
    if mb.status == mb.last_turn:
        return 2

    markpats = mb.enum_markpats()
    # 相手が勝利できる場合は評価値として -1 を返す
    if Markpat(last_turn=0, turn=2, empty=1) in markpats:
        return -1
    # 次の自分の手番で自分が勝利できる場合は評価値として 1 を返す
    elif Markpat(last_turn=2, turn=0, empty=1) in markpats:
        return 1
    # それ以外の場合は評価値として 0 を返す
    else:
        return 0

@ai_by_score
def ai9s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、以下のルールで着手を行う AI.

    以下のルールで着手を行う
    1. 真ん中のマスに優先的に着手する
    2. そうでない場合は、勝てる場合に勝つ
    3. そうでない場合は、相手が勝利できる着手を行わない
    4. そうでない場合は、次 の 自分の手番で必ず勝利できるように、
       「自 2 敵 0 空 1」が 2 つ以上存在する着手を行う
    5. そうでない場合は、次の自分の手番で勝利できるように、
       「自 2 敵 0 空 1」が 1 つ存在する局面になる着手を行う
    6. そうでない場合はランダムなマスに着手する    
  
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """    
    
    # 真ん中のマスに着手している場合は、評価値として 4 を返す
    if mb.last_move == (1, 1):
        return 4

    # 自分が勝利している場合は、評価値として 3 を返す
    if mb.status == mb.last_turn:
        return 3

    markpats = mb.count_markpats()
    if debug:
        pprint(markpats)
    # 相手が勝利できる場合は評価値として -1 を返す
    if markpats[Markpat(last_turn=0, turn=2, empty=1)] > 0:
        return -1
    # 次の自分の手番で自分が必ず勝利できる場合は評価値として 2 を返す
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] >= 2:
        return 2
    # 次の自分の手番で自分が勝利できる場合は評価値として 1 を返す
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] == 1:
        return 1
    # それ以外の場合は評価値として 0 を返す
    else:
        return 0

@ai_by_score
def ai10s(mb:Marubatsu, debug:bool=False) -> float:
    """評価関数を利用したアルゴリズムで、以下のルールで着手を行う AI.

    以下のルールで着手を行う
    1. 真ん中のマスに優先的に着手する
    2. そうでない場合は、勝てる場合に勝つ
    3. そうでない場合は、相手が勝利できる着手を行わない
    4. そうでない場合は、次 の 自分の手番で必ず勝利できるように、
       「自 2 敵 0 空 1」が 2 つ以上存在する着手を行う
    5. そうでない場合は、以下の条件の組み合わせで着手を行う
      5.1. 次の自分の手番で勝利できるように、
          「自 2 敵 0 空 1」が 1 つ存在する局面になる着手を行う
      5.2. 次の自分の手番で有利になるように、
          「自 1 敵 0 空 2」が最も多くなる局面になる着手を行う
    6. そうでない場合はランダムなマスに着手する    
  
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """   
    
    # 真ん中のマスに着手している場合は、評価値として 300 を返す
    if mb.last_move == (1, 1):
        return 300

    # 自分が勝利している場合は、評価値として 200 を返す
    if mb.status == mb.last_turn:
        return 200

    markpats = mb.count_markpats()
    if debug:
        pprint(markpats)
    # 相手が勝利できる場合は評価値として -100 を返す
    if markpats[Markpat(last_turn=0, turn=2, empty=1)] > 0:
        return -100
    # 次の自分の手番で自分が必ず勝利できる場合は評価値として 100 を返す
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] >= 2:
        return 100

    # 評価値の合計を計算する変数を 0 で初期化する
    score = 0        
    # 次の自分の手番で自分が勝利できる場合は評価値に 1 を加算する
    if markpats[Markpat(last_turn=2, turn=0, empty=1)] == 1:
        score += 1
    # 「自 1 敵 0 空 2」の数だけ、評価値を加算する
    score += markpats[Markpat(last_turn=1, turn=0, empty=2)]
    
    # 計算した評価値を返す
    return score

@ai_by_score
def ai11s(mb:Marubatsu, debug:bool=False, score_201:float=2, score_102:float=0.5, score_012:float=-1) -> float:
    """以下のルールで着手を行う AI の評価関数.
   
    以下のルールで着手を行う
    1. 真ん中のマスに優先的に着手する（評価値 300）
    2. そうでない場合は、勝てる場合に勝つ（評価値 200）
    3. そうでない場合は、相手が勝利できる着手を行わない（評価値 -100）
    4. そうでない場合は、次 の 自分の手番で必ず勝利できるように、
       「自 2 敵 0 空 1」が 2 つ以上存在する着手を行う（評価値 100）
    5. そうでない場合は、以下の条件の組み合わせで着手を行う（評価値 は下記の合計）
      5.1. 次の自分の手番で勝利できるように、
          「自 2 敵 0 空 1」が 1 つ存在する局面になる着手を行う（評価値 score_201）
      5.2. 次の自分の手番で有利になるように、
          「自 1 敵 0 空 2」が最も多くなる局面になる着手を行う（評価値 1 つあたり score_102）
      5.3. 次の自分の手番で有利になるように、
          「自 0 敵 1 空 2」が最も少なくなる局面になる着手を行う（評価値 1 つあたり score_012）
    6. そうでない場合はランダムなマスに着手する    
      
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        score_xxx:
            評価値のパラメータ、詳細は、上記のルールの説明を参照
            
    Returns:
        mb の局面の評価値
    """

    # 真ん中のマスに着手している場合は、評価値として 300 を返す
    if mb.last_move == (1, 1):
        return 300

    # 自分が勝利している場合は、評価値として 200 を返す
    if mb.status == mb.last_turn:
        return 200

    markpats = mb.count_markpats()
    if debug:
        pprint(markpats)
    # 相手が勝利できる場合は評価値として -100 を返す
    if markpats[Markpat(last_turn=0, turn=2, empty=1)] > 0:
        return -100
    # 次の自分の手番で自分が必ず勝利できる場合は評価値として 100 を返す
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] >= 2:
        return 100

    # 評価値の合計を計算する変数を 0 で初期化する
    score = 0        
    # 次の自分の手番で自分が勝利できる場合は評価値に score_201 を加算する
    if markpats[Markpat(last_turn=2, turn=0, empty=1)] == 1:
        score += score_201
    # 「自 1 敵 0 空 2」1 つあたり score_102 だけ、評価値を加算する
    score += markpats[Markpat(last_turn=1, turn=0, empty=2)] * score_102
    # 「自 0 敵 1 空 2」1 つあたり score_201 だけ、評価値を減算する
    score += markpats[Markpat(last_turn=0, turn=1, empty=2)] * score_012
    
    # 計算した評価値を返す
    return score

@ai_by_score
def ai12s(mb:Marubatsu, debug:bool=False, score_victory:float=300, score_sure_victory:float=200, \
          score_defeat:float=-100, score_special:float=100, score_201:float=2, \
          score_102:float=0.5, score_012:float=-1) -> float:
    """評価関数を利用したアルゴリズムで、以下のルールで着手を行う AI.

    以下のルールで着手を行う
    1. 勝てる場合に勝つ（評価値 score_victory）
    2. そうでない場合は、相手が勝利できる着手を行わない（評価値 score_defeat）
    3. そうでない場合は、次 の 自分の手番で必ず勝利できるように、
       「自 2 敵 0 空 1」が 2 つ以上存在する着手を行う（評価値 score_sure_victory）
    4. そうでない場合は、斜め方向に 〇×〇 が 並び、他の 6 マスが
       空のマスの場合は、いずれかの辺のマスに着手を行う（評価値 score_special）       
    5. そうでない場合は、以下の条件の組み合わせで着手を行う（評価値 は下記の合計）
      5.1. 次の自分の手番で勝利できるように、
          「自 2 敵 0 空 1」が 1 つ存在する局面になる着手を行う（評価値 score_201）
      5.2. 次の自分の手番で有利になるように、
          「自 1 敵 0 空 2」が最も多くなる局面になる着手を行う（評価値 1 つあたり score_102）
      5.3. 次の自分の手番で有利になるように、
          「自 0 敵 1 空 2」が最も少なくなる局面になる着手を行う（評価値 1 つあたり score_012）
    6. そうでない場合はランダムなマスに着手する    
      
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        score_xxx:
            評価値のパラメータ、詳細は、上記のルールの説明を参照
            
    Returns:
        mb の局面の評価値
    """
     
    # 自分が勝利している場合
    if mb.status == mb.last_turn:
        return score_victory

    markpats = mb.count_markpats()
    if debug:
        pprint(markpats)
    # 相手が勝利できる場合
    if markpats[Markpat(last_turn=0, turn=2, empty=1)] > 0:
        return score_defeat
    # 次の自分の手番で自分が必ず勝利できる場合
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] >= 2:
        return score_sure_victory
    
    # 斜め方向に 〇×〇 が並び、いずれかの辺の 1 つのマスのみに × が配置されている場合
    if mb.board[1][1] == Marubatsu.CROSS and \
        (mb.board[0][0] == mb.board[2][2] == Marubatsu.CIRCLE or \
        mb.board[2][0] == mb.board[0][2] == Marubatsu.CIRCLE) and \
        (mb.board[1][0] == Marubatsu.CROSS or \
        mb.board[0][1] == Marubatsu.CROSS or \
        mb.board[2][1] == Marubatsu.CROSS or \
        mb.board[1][2] == Marubatsu.CROSS) and \
        mb.move_count == 4:
        return score_special    

    # 評価値の合計を計算する変数を 0 で初期化する
    score = 0        
    # 次の自分の手番で自分が勝利できる場合は評価値に score_201 を加算する
    if markpats[Markpat(last_turn=2, turn=0, empty=1)] == 1:
        score += score_201
    # 「自 1 敵 0 空 2」1 つあたり score_102 だけ、評価値を加算する
    score += markpats[Markpat(last_turn=1, turn=0, empty=2)] * score_102
    # 「自 0 敵 1 空 2」1 つあたり score_201 だけ、評価値を減算する
    score += markpats[Markpat(last_turn=0, turn=1, empty=2)] * score_012
    
    # 計算した評価値を返す
    return score

@ai_by_score
def ai13s(mb:Marubatsu, debug:bool=False, score_victory:float=300, score_sure_victory:float=200, \
          score_defeat:float=-100, score_special:float=100, score_201:float=2, \
          score_102:float=0.5, score_012:float=-1) -> float:
    """評価関数を利用したアルゴリズムで、以下のルールで着手を行う AI.

    以下のルールで着手を行う
    1. 勝てる場合に勝つ（評価値 score_victory）
    2. そうでない場合は、相手が勝利できる着手を行わない（評価値 score_defeat * 「自 0 敵 2 空 1」の数）
    3. そうでない場合は、次 の 自分の手番で必ず勝利できるように、
       「自 2 敵 0 空 1」が 2 つ以上存在する着手を行う（評価値 score_sure_victory）
    4. そうでない場合は、斜め方向に 〇×〇 が 並び、他の 6 マスが
       空のマスの場合は、いずれかの辺のマスに着手を行う（評価値 score_special）       
    5. そうでない場合は、以下の条件の組み合わせで着手を行う（評価値 は下記の合計）
      5.1. 次の自分の手番で勝利できるように、
          「自 2 敵 0 空 1」が 1 つ存在する局面になる着手を行う（評価値 score_201）
      5.2. 次の自分の手番で有利になるように、
          「自 1 敵 0 空 2」が最も多くなる局面になる着手を行う（評価値 1 つあたり score_102）
      5.3. 次の自分の手番で有利になるように、
          「自 0 敵 1 空 2」が最も少なくなる局面になる着手を行う（評価値 1 つあたり score_012）
    6. そうでない場合はランダムなマスに着手する    
      
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        score_xxx:
            評価値のパラメータ、詳細は、上記のルールの説明を参照
            
    Returns:
        mb の局面の評価値
    """

    # 自分が勝利している場合
    if mb.status == mb.last_turn:
        return score_victory

    markpats = mb.count_markpats()
    if debug:
        pprint(markpats)
    # 相手が勝利できる場合
    if markpats[Markpat(last_turn=0, turn=2, empty=1)] > 0:
        return score_defeat * markpats[Markpat(last_turn=0, turn=2, empty=1)]
    # 次の自分の手番で自分が必ず勝利できる場合
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] >= 2:
        return score_sure_victory
    
    # 斜め方向に 〇×〇 が並び、いずれかの辺の 1 つのマスのみに × が配置されている場合
    if mb.board[1][1] == Marubatsu.CROSS and \
        (mb.board[0][0] == mb.board[2][2] == Marubatsu.CIRCLE or \
        mb.board[2][0] == mb.board[0][2] == Marubatsu.CIRCLE) and \
        (mb.board[1][0] == Marubatsu.CROSS or \
        mb.board[0][1] == Marubatsu.CROSS or \
        mb.board[2][1] == Marubatsu.CROSS or \
        mb.board[1][2] == Marubatsu.CROSS) and \
        mb.move_count == 4:
        return score_special    

    # 評価値の合計を計算する変数を 0 で初期化する
    score = 0        
    # 次の自分の手番で自分が勝利できる場合は評価値に score_201 を加算する
    if markpats[Markpat(last_turn=2, turn=0, empty=1)] == 1:
        score += score_201
    # 「自 1 敵 0 空 2」1 つあたり score_102 だけ、評価値を加算する
    score += markpats[Markpat(last_turn=1, turn=0, empty=2)] * score_102
    # 「自 0 敵 1 空 2」1 つあたり score_201 だけ、評価値を減算する
    score += markpats[Markpat(last_turn=0, turn=1, empty=2)] * score_012
    
    # 計算した評価値を返す
    return score

@ai_by_score
def ai14s(mb:Marubatsu, debug:bool=False, score_victory:float=300, score_sure_victory:float=200, \
          score_defeat:float=-100, score_special:float=100, score_201:float=2, \
          score_102:float=0.5, score_012:float=-1) -> float:
    """評価関数を利用したアルゴリズムで、以下のルールで着手を行う AI.

    以下のルールで着手を行う
    1. 勝てる場合に勝つ（評価値 score_victory）
    2. そうでない場合は、相手が勝利できる着手を行わない（評価値 score_defeat * 「自 0 敵 2 空 1」の数 に、下記の 5 の評価値を加算する）
    3. そうでない場合は、次 の 自分の手番で必ず勝利できるように、
       「自 2 敵 0 空 1」が 2 つ以上存在する着手を行う（評価値 score_sure_victory）
    4. そうでない場合は、斜め方向に 〇×〇 が 並び、他の 6 マスが
       空のマスの場合は、いずれかの辺のマスに着手を行う（評価値 score_special）       
    5. そうでない場合は、以下の条件の組み合わせで着手を行う（評価値 は下記の合計）
      5.1. 次の自分の手番で勝利できるように、
          「自 2 敵 0 空 1」が 1 つ存在する局面になる着手を行う（評価値 score_201）
      5.2. 次の自分の手番で有利になるように、
          「自 1 敵 0 空 2」が最も多くなる局面になる着手を行う（評価値 1 つあたり score_102）
      5.3. 次の自分の手番で有利になるように、
          「自 0 敵 1 空 2」が最も少なくなる局面になる着手を行う（評価値 1 つあたり score_012）
    6. そうでない場合はランダムなマスに着手する    
      
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        score_xxx:
            評価値のパラメータ、詳細は、上記のルールの説明を参照
            
    Returns:
        mb の局面の評価値
    """
        
    # 評価値の合計を計算する変数を 0 で初期化する
    score = 0        

    # 自分が勝利している場合
    if mb.status == mb.last_turn:
        return score_victory

    markpats = mb.count_markpats()
    if debug:
        pprint(markpats)
    # 相手が勝利できる場合は評価値を加算する
    if markpats[Markpat(last_turn=0, turn=2, empty=1)] > 0:
        score = score_defeat * markpats[Markpat(last_turn=0, turn=2, empty=1)]
    # 次の自分の手番で自分が必ず勝利できる場合
    elif markpats[Markpat(last_turn=2, turn=0, empty=1)] >= 2:
        return score_sure_victory
    
    # 斜め方向に 〇×〇 が並び、いずれかの辺の 1 つのマスのみに × が配置されている場合
    if mb.board[1][1] == Marubatsu.CROSS and \
        (mb.board[0][0] == mb.board[2][2] == Marubatsu.CIRCLE or \
        mb.board[2][0] == mb.board[0][2] == Marubatsu.CIRCLE) and \
        (mb.board[1][0] == Marubatsu.CROSS or \
        mb.board[0][1] == Marubatsu.CROSS or \
        mb.board[2][1] == Marubatsu.CROSS or \
        mb.board[1][2] == Marubatsu.CROSS) and \
        mb.move_count == 4:
        return score_special    

    # 次の自分の手番で自分が勝利できる場合は評価値に score_201 を加算する
    if markpats[Markpat(last_turn=2, turn=0, empty=1)] == 1:
        score += score_201
    # 「自 1 敵 0 空 2」1 つあたり score_102 だけ、評価値を加算する
    score += markpats[Markpat(last_turn=1, turn=0, empty=2)] * score_102
    # 「自 0 敵 1 空 2」1 つあたり score_201 だけ、評価値を減算する
    score += markpats[Markpat(last_turn=0, turn=1, empty=2)] * score_012
    
    # 計算した評価値を返す
    return score

@ai_by_candidate
def ai_gt1(mb:Marubatsu, debug:bool=False, mbtree:Mbtree|None=None) -> list[tuple[int, int]]:
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        mbtree:
            評価値が計算されている Mbtree クラスのインスタンス
            
    Returns:
        候補手の一覧を表す list
    """    

    node = mbtree.root
    for move in mb.records[1:]:
        node = node.children_by_move[move]

    bestmoves = []
    for move, childnode in node.children_by_move.items():
        if node.score == childnode.score:
            bestmoves.append(move)
    return bestmoves

@ai_by_candidate
def ai_gt2(mb:Marubatsu, debug:bool=False, mbtree:Mbtree|None=None) -> list[tuple[int, int]]:
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        mbtree:
            評価値が計算されている Mbtree クラスのインスタンス
            
    Returns:
        候補手の一覧を表す list
    """
    
    node = mbtree.root
    for move in mb.records[1:]:
        node = node.children_by_move[move]

    return node.bestmoves

@ai_by_candidate
def ai_gt3(mb:Marubatsu, debug:bool=False, mbtree:Mbtree|None=None) -> list[tuple[int, int]]:
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        mbtree:
            評価値が計算されている Mbtree クラスのインスタンス
            
    Returns:
        候補手の一覧を表す list
    """

    node = mbtree.nodelist_by_mb[tuple(mb.records)]
    return node.bestmoves

@ai_by_candidate
def ai_gt4(mb:Marubatsu, debug:bool=False, mbtree:Mbtree|None=None) -> list[tuple[int, int]]:
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        mbtree:
            評価値が計算されている Mbtree クラスのインスタンス
            
    Returns:
        候補手の一覧を表す list
    """
    
    return mbtree.bestmoves_by_mb[tuple(mb.records)]

@ai_by_candidate
def ai_gt5(mb:Marubatsu, debug:bool=False, bestmoves:dict[tuple, list[tuple[int, int]]]|None=None) -> list[tuple[int, int]]:
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる
    
    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        bestmoves:
            局面の棋譜を表す Marubatsu クラスの `records` 属性をキーとし、
            そのキーの値にその局面の最善手の一覧を記録する dict
            
    Returns:
        候補手の一覧を表す list
    """
    
    return choice(bestmoves[tuple(mb.records)])

@ai_by_candidate
def ai_gt6(mb:Marubatsu, debug:bool=False, bestmoves_by_board:dict[str, list[tuple[int, int]]]|None=None) -> list[tuple[int, int]]:
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    ai_by_candidate のデコレーターでデコレートするので、
    ai_by_candidate の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        bestmoves_by_board:
            局面のゲーム盤の状態を Marubatsu クラスの `board` 属性を文字列に変換したものをキーとし、
            そのキーの値にその局面の最善手の一覧を記録する dict
                        
    Returns:
        候補手の一覧を表す list
    """
    
    return bestmoves_by_board[mb.board_to_str()]

def ai_gt7(mborig:Marubatsu, debug:bool=False, bestmoves_and_score_by_board:dict=None, rand:bool=True, analyze:bool=False):
    """評価が計算されたゲーム木を使って最善手を選択する強解決の AI.

    Args:
        mborig: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
        bestmoves_and_score_by_board:
            局面のゲーム盤の状態を Marubatsu クラスの `board` 属性を文字列に変換したものをキーとし、
            そのキーの値にその局面の最善手の一覧とそれぞれの合法種に着手を行った局面の評価値の一覧を記録する dict
        rand:
            True の場合は、最善手の中からランダムで着手を選択する
            False の場合は、先頭の最善手の着手を選択する
        analyze:
            False の場合に、着手する座標を表す tuple を返す
            True の場合に、候補手の一覧と、それぞれの合法手に着手した場合の評価値を
            表す下記の dict を返す
                candidate: 
                    候補手の一覧を表す list
                score_by_move: 
                    合法手をキーとし、そのキーの値に合法手を着手した場合の
                    評価値を代入した dict                        

    Returns:
        候補手の一覧を表す list など。詳細は Args を参照
    """

    candidate = bestmoves_and_score_by_board[mborig.board_to_str()]["bestmoves"]
    dprint(debug, "candidate", candidate)
    if analyze:
        legal_moves = mborig.calc_legal_moves()
        score_by_move = {}
        for move in legal_moves:
            mb = deepcopy(mborig)
            x, y = move
            mb.move(x, y)
            score_by_move[move] = bestmoves_and_score_by_board[mb.board_to_str()]["score"]
        dprint(debug, "score_by_move", score_by_move) 
        return {
            "candidate": candidate, 
            "score_by_move": score_by_move
        }
    else:
        if rand:
            return choice(candidate)
        else:
            return candidate[0]
        
@ai_by_score
def ai_mmdfs(mb, debug=False):
    """ミニマックス法で評価値を動的に計算する強解決の AI
      
    ai_by_score のデコレーターでデコレートするので、
    ai_by_score の仮引数も利用できる

    Args:
        mb: 
            現在の局面を表す Marubatsu クラスのインスタンス
        debug:
            True の場合にデバッグ表示を行う
            
    Returns:
        mb の局面の評価値
    """
    
    count = 0
    def mm_search(mborig):
        nonlocal count
        count += 1
        if mborig.status == Marubatsu.CIRCLE:
            return 1
        elif mborig.status == Marubatsu.CROSS:
            return -1
        elif mborig.status == Marubatsu.DRAW:
            return 0
        
        legal_moves = mborig.calc_legal_moves()
        score_list = []
        for x, y in legal_moves:
            mb = deepcopy(mborig)
            mb.move(x, y)
            score_list.append(mm_search(mb))
        if mborig.turn == Marubatsu.CIRCLE:
            return max(score_list)
        else:
            return min(score_list)
    
    score = mm_search(mb)
    dprint(debug, "count =", count)
    if mb.turn == Marubatsu.CIRCLE:
        score *= -1
    return score