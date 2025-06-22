from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from marubatsu import Marubatsu, Marubatsu_GUI
from gui import GUI
import ipywidgets as widgets
import gzip
import pickle
from tqdm import tqdm
from collections import defaultdict
from itertools import product

class Rect:
    """ 長方形を表すクラス
    
    Attributes:
        x(float):
            長方形の左上の点の x 座標
        y(float):
            長方形の左上の点の y 座標
        width(float):
            長方形の幅
        height(float):
            長方形の高さ    
    """
    
    def __init__(self, x:float, y:float, width:float, height:float):
        """ イニシャライザ.
        
        Args:
            x:
                長方形の左上の点の x 座標
            y:
                長方形の左上の点の y 座標
            width:
                長方形の幅
            height:
                長方形の高さ   
        """
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def __str__(self):
        return f"Rectangle ({self.x}, {self.y}) width = {self.width} height = {self.height}"        

    def is_inside(self, x:float, y:float) -> bool:
        """(x, y) が長方形の内部の点であるかの判定.
        
        Args:
            x:
                判定する点の x 座標
            y:
                判定する点の y 座標
                
        Returns:
            長方形の内部の場合は True, そうでなければ False
        """
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

class Node:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        クラス属性    
        count(int):
            ノードが作成された回数を表す
        
        インスタンス属性
        id(int):
            ノードの識別子。ノードを作成した順番でつけられる
        mb(Marubatsu):
            このノードの局面を表す Marubatsu クラスのインスタンス
        depth(int):
            このノードのゲーム木内での深さ
        height(float):
            このノードを描画した際の高さ
        childlen (list[Node]):
            子ノードの一覧を表す list
        childlen_by_move (dict[tuple, Node]):
            子ノードの一覧を表す list            
        bestmoves(list[tuple[int, int]]):
            この局面の最善手の一覧
    """
    
    # ノードを作成した回数を表すクラス属性
    count = 0
    
    def __init__(self, mb:Marubatsu, parent=None, depth:int=0, bestmoves_and_score_by_board:dict|None=None):
        """ イニシャライザ.
        
        Args:
            mb:
                このノードの局面を表す Marubatsu クラスのインスタンス
            parent:
                親ノード。None の場合は親ノードが存在しないことを意味する
            depth:
                深さ
            bestmoves_and_score_by_board:
                局面と最善手・評価値の対応表を表す dict
                None でない場合は、このデータを使ってこのノードの局面の最善手を
                計算して bestmoves 属性に代入する
        """

        self.id = Node.count
        Node.count += 1
        self.mb = mb
        self.parent = parent
        self.depth = depth
        self.children = []
        self.children_by_move = {}   
        if bestmoves_and_score_by_board is not None:
            bestmoves_and_score = bestmoves_and_score_by_board[self.mb.board_to_str()]
            self.bestmoves = bestmoves_and_score["bestmoves"]
            self.score = bestmoves_and_score["score"]       
        
    def insert(self, node):
        """ 子ノードを挿入する.
        
        Args:
            node(Node):
                挿入する Node クラスのインスタンス
        """

        self.children.append(node)
        self.children_by_move[node.mb.last_move] = node
        
    def calc_children(self, bestmoves_and_score_by_board:dict|None=None):
        """子ノードを計算する
        
        Args:
            bestmoves_and_score_by_board:
                局面と最善手・評価値の対応表を表す dict
        """
        
        self.children = []
        for x, y in self.mb.calc_legal_moves():
            childmb = deepcopy(self.mb)
            childmb.move(x, y)
            self.insert(Node(childmb, parent=self, depth=self.depth + 1,
                            bestmoves_and_score_by_board=bestmoves_and_score_by_board))
            
        
    def calc_height(self):
        """ノードを描画した際の高さを計算する."""
        
        if len(self.children) == 0:
            self.height = 4
        else:
            self.height = 0
            for childnode in self.children:
                self.height += childnode.height

    def draw_node(self, ax=None, maxdepth:int|None=None, emphasize:bool=False, darkness:float=0, 
                  show_score:bool=True, size:float=0.25, lw:float=0.8, dx:float=0, dy:float=0) -> Rect:
        """ノードと子ノードの関係を描画する.
               
        Args:
            ax:
                None の場合は、Figure を作成し、このノードと子ノードの関係のみを描画する
                None でない場合は ax に、ノードの高さを考慮して描画する。そのため、
                あらかじめノードの高さを計算しておく必要がある
            maxdepth:
                子ノードをしないノードの深さ
            emphasize:
                True の場合にノードを強調して表示する
            darkness:
                描画するノードの暗さを表す 0 ～ 1 の数値。数字が大きいほど暗く表示する
            show_score:
                True の場合に、評価値を表示する
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
            dx:
                描画する Axes 上の x 座標
            dy:
                描画する Axes 上の y 座標
                
        Returns:
            描画したノードの描画範囲を表す Rect
        """            
        
        width = 8
        if ax is None:
            height = len(self.children) * 4
            fig, ax = plt.subplots(figsize=(width * size, height * size))
            ax.set_xlim(0, width)
            ax.set_ylim(0, height)   
            ax.invert_yaxis()
            ax.axis("off")
            for childnode in self.children:
                childnode.height = 4
            self.height = height         
            
        # 自分自身のノードを真ん中の位置になるように (dx, dy) からずらして描画する
        y = dy + (self.height - 3) / 2
        bc = "red" if emphasize else None
        Marubatsu_GUI.draw_board(ax, self.mb, show_result=True, 
                                score=getattr(self, "score", None), bc=bc, darkness=darkness, lw=lw, dx=dx, dy=y)
        if hasattr(self, "score") and show_score:
            ax.text(dx, y - 0.1, self.score, fontsize=70*size)
        rect = Rect(dx, y, 3, 3)
        # 子ノードが存在する場合に、エッジの線と子ノードを描画する
        if len(self.children) > 0:
            if maxdepth != self.depth:   
                ax.plot([dx + 3.5, dx + 4], [y + 1.5, y + 1.5], c="k", lw=lw)
                prevy = None
                for childnode in self.children:
                    childnodey = dy + (childnode.height - 3) / 2
                    if maxdepth is None:
                        Marubatsu_GUI.draw_board(ax, childnode.mb, show_result=True,
                                                score=getattr(childnode, "score", None), dx=dx+5, dy=childnodey, lw=lw)
                    edgey = childnodey + 1.5
                    ax.plot([dx + 4 , dx + 4.5], [edgey, edgey], c="k", lw=lw)
                    if prevy is not None:
                        ax.plot([dx + 4 , dx + 4], [prevy, edgey], c="k", lw=lw)
                    prevy = edgey
                    dy += childnode.height
            else:
                ax.plot([dx + 3.5, dx + 4.5], [y + 1.5, y + 1.5], c="k", lw=lw)
                
        return rect

class Mbtree:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        root(Node):
            ルートノード
        algo(str):
            ゲーム木を作成するアルゴリズムを表す文字列
            "bf": 幅優先アルゴリズム
            それ以外：深さ優先アルゴリズム
        nodelist(list[Node])
            ゲーム木に登録された順にノードが格納されている list
        nodelist_by_depth(list[list[Node]]):
            各深さのノードの list を記録する list
        nodenum(int):
            ゲーム木のノードの総数
        nodelist_by_score(list[Node])
            評価値を計算する過程で処理が行われたノードの順番を記録する list
        ablist_by_score(list[tuple[float float, str]])
            評価値を計算する過程で処理が行われた (α 値, β 値, 子ノードの評価値, メッセージ) を表す tuple を記録する list
        nodelist_by_mb(dict[tuple])
            Marubatsu クラスの棋譜を表す records 属性をキーとし、
            キーの値に対応するノードを代入する dict
        bestmoves_by_mb(dict[tuple])
            Marubatsu クラスの棋譜を表す records 属性をキーとし、
            キーの値に対応するノードの最善手の一覧を代入する dict
    """
    
    def __init__(self, algo:str="bf", shortest_victory:bool=False, 
                 recalculate_draw_score=False, subtree:dict|None=None):
        """イニシャライザ.
        
        Args:
            algo:
                ゲーム木を生成するアルゴリズムを表す文字列
                "bf" の場合は幅優先アルゴリズムで生成する
                それ以外の場合は深さ優先アルゴリズムで生成する        
            shortest_victory:
                True の場合に、最短で勝利するように評価値を計算する
            recalculate_draw_score:
                引き分けの局面の評価値を、勝利できる可能性がある場合を
                考慮した評価値として再計算する
            subtree:
                None の場合はゲーム木全体を作成する
                dict が代入されている場合は、他の仮引数の値をすべて無視して
                部分木を作成する。dict のキーとキーの値の意味については
                create_subtree の説明を参照すること
        """
        
        if subtree is not None:
            self.subtree = subtree
            self.create_subtree()
            return

        self.algo = algo
        self.shortest_victory = shortest_victory
        self.recalculate_draw_score = recalculate_draw_score
        Node.count = 0
        self.root = Node(Marubatsu())
        if self.algo == "bf":  
            self.create_tree_by_bf()
            self.calc_score_by_bf()
        else:
            self.nodelist = [self.root]
            self.nodelist_by_depth = [[] for _ in range(10)]
            self.nodelist_by_depth[0].append(self.root)
            self.nodenum = 0
            self.create_tree_by_df(self.root)
            self.nodelist_by_score = []
            self.calc_score_by_df(self.root)
        if self.recalculate_draw_score:
            self.recalculate_score()
        self.nodelist_by_mb = {}
        self.bestmoves_by_mb = {}
        self.calc_bestmoves(self.root)
           
    def create_tree_by_bf(self):
        """幅優先アルゴリズムによるゲーム木の作成."""
        
        # 深さ 0 のノードを、子ノードを作成するノードのリストに登録する
        nodelist = [self.root]
        depth = 0
        # 各深さのノードのリストを記録する変数を初期化する
        self.nodelist_by_depth = [ nodelist ]
        
        # 深さ depth のノードのリストが空になるまで繰り返し処理を行う
        while len(nodelist) > 0:
            childnodelist = [] 
            for node in nodelist:
                if node.mb.status == Marubatsu.PLAYING:
                    node.calc_children()
                    childnodelist += node.children
            self.nodelist_by_depth.append(childnodelist)
            nodelist = childnodelist
            depth += 1
            print(f"{len(nodelist):>6} depth {depth} node created")
            
        self.nodenum = 0
        self.nodelist = []
        for nodelist in self.nodelist_by_depth:
            self.nodenum += len(nodelist)
            self.nodelist += nodelist
        print(f"total node num = {self.nodenum}")
        
    def create_tree_by_df(self, N:Node):
        """深さ優先アルゴリズムによるゲーム木の再起呼び出しによる作成.
        
        Args:
            N:
                子ノードを作成するノード
        """

        legal_moves = N.mb.calc_legal_moves()
        for x, y in legal_moves:
            mb = deepcopy(N.mb)
            mb.move(x, y)
            node = Node(mb, parent=N, depth=N.depth + 1)
            N.insert(node)
            self.nodelist.append(node)
            self.nodelist_by_depth[node.depth].append(node)
            self.nodenum += 1
            self.create_tree_by_df(node)

    def calc_score_of_node(self, node:Node):
        """ ノードの評価値を計算し、score 属性に代入する
                
        Args:
            node:
                評価値を計算するノード
        """
        
        if node.mb.status == Marubatsu.CIRCLE:
            node.score = (11 - node.depth) / 2 if self.shortest_victory else 1
        elif node.mb.status == Marubatsu.DRAW:
            node.score = 0
        elif node.mb.status == Marubatsu.CROSS:
            node.score = (node.depth - 10) / 2 if self.shortest_victory else -1
        node.max_score = node.score
        node.min_score = node.score
        
    def calc_score_by_bf(self):
        """幅優先アルゴリズムによるゲーム木の評価値の計算."""        
        
        self.nodelist_by_score = self.nodelist[:]
        for nodelist in reversed(self.nodelist_by_depth):
            for node in nodelist:
                if node.mb.status != Marubatsu.PLAYING:
                    self.calc_score_of_node(node)
                else:
                    score_list = [childnode.score for childnode in node.children]
                    if node.mb.move_count % 2 == 0:
                        score = max(score_list)
                    else:
                        score = min(score_list)
                    node.score = score
                    node.max_score = max([childnode.max_score for childnode in node.children])
                    node.min_score = min([childnode.min_score for childnode in node.children])
                self.nodelist_by_score.append(node)
                node.score_index = len(self.nodelist_by_score) - 1    
                
    def calc_score_by_df(self, node:Node) -> tuple[float, float, float]:
        """深さ優先アルゴリズムによるゲーム木の評価値の計算.
        
        Args:
            node:
                評価値を計算するノード
        
        Returns:
            このノードの評価値、最大の評価値、最小の評価値
        """
                
        self.nodelist_by_score.append(node)
        if node.mb.status != Marubatsu.PLAYING:
            self.calc_score_of_node(node)
        else:
            score_list = []
            max_score_list = []
            min_score_list = []
            for childnode in node.children:
                score, max_score, min_score = self.calc_score_by_df(childnode)
                score_list.append(score)
                max_score_list.append(max_score)
                min_score_list.append(min_score)
                self.nodelist_by_score.append(node)
            if node.mb.move_count % 2 == 0:
                score = max(score_list)
            else:
                score = min(score_list)
            node.score = score
            node.max_score = max(max_score_list)
            node.min_score = min(min_score_list)
            
        self.nodelist_by_score.append(node)
        node.score_index = len(self.nodelist_by_score) - 1        
        return node.score, node.max_score, node.min_score     
    
    def calc_score_by_ab(self, abroot:Node, debug:bool=False, minimax:bool=False, init_ab:bool=False, use_tt:bool=False):
        """αβ 法によるゲーム木の評価値の計算。ミニマックス法にも対応.
        
        Args:
            abroot:
                評価値を計算するノード
            minimax:
                True の場合にミニマックス法で評価値を計算する
            init_ab:
                True の場合に α 値と β 値の初期値を評価値の最小値と最大値で初期化する
            use_tt:
                True の場合に置換表を利用する
            debug:
                True の場合に評価値を計算したノードを表示する
        """
             
        def assign_pruned_index(node, index):
            node.pruned_index = index
            self.num_pruned += 1
            for childnode in node.children:
                assign_pruned_index(childnode, index)
            
        def calc_ab_score(node, tt, alpha=float("-inf"), beta=float("inf")):
            if minimax:
                alpha = float("-inf")
                beta = float("inf")
            if use_tt:
                boardtxt = node.mb.board_to_str()
                key = (boardtxt, alpha, beta)
                if key in tt:
                    node.score = tt[key]
                    if node.mb.turn == Marubatsu.CIRCLE:
                        alpha = node.score
                    else:
                        beta = node.score
                    self.nodelist_by_score.append(node)
                    self.num_calculated += 1     
                    for childnode in node.children:
                        assign_pruned_index(childnode, len(self.nodelist_by_score) - 1)
                    self.ablist_by_score.append((alpha, beta, None, "tt",
                                                self.num_calculated, self.num_pruned))
                    node.score_index = len(self.nodelist_by_score) - 1  
                    return node.score
                    
            self.nodelist_by_score.append(node)
            self.ablist_by_score.append((alpha, beta, None, "start",
                                        self.num_calculated, self.num_pruned))
            if node.mb.status != Marubatsu.PLAYING:
                self.calc_score_of_node(node)
                if node.mb.turn == Marubatsu.CIRCLE:
                    alpha = node.score
                else:
                    beta = node.score
            else:
                if node.mb.turn == Marubatsu.CIRCLE:
                    for childnode in node.children:
                        score = calc_ab_score(childnode, tt, alpha, beta)
                        self.nodelist_by_score.append(node)
                        self.ablist_by_score.append((alpha, beta, score, "score",
                                                    self.num_calculated, self.num_pruned))
                        if score > alpha:
                            alpha = score
                        self.nodelist_by_score.append(node)
                        if score >= beta:
                            index = node.children.index(childnode)
                            for prunednode in node.children[index + 1:]:
                                assign_pruned_index(prunednode, len(self.nodelist_by_score) - 1)
                        self.ablist_by_score.append((alpha, beta, None, "update",
                                                    self.num_calculated, self.num_pruned))
                        if score >= beta:
                            break
                    node.score = alpha
                else:
                    for childnode in node.children:
                        score = calc_ab_score(childnode, tt, alpha, beta)
                        self.nodelist_by_score.append(node)
                        self.ablist_by_score.append((alpha, beta, score, "score",
                                                    self.num_calculated, self.num_pruned))
                        if score < beta:
                            beta = score
                        self.nodelist_by_score.append(node)
                        if score <= alpha:
                            index = node.children.index(childnode)
                            for prunednode in node.children[index + 1:]:
                                assign_pruned_index(prunednode, len(self.nodelist_by_score) - 1)
                        self.ablist_by_score.append((alpha, beta, None, "update",
                                                    self.num_calculated, self.num_pruned))
                        if score <= alpha:
                            break
                    node.score = beta

            self.nodelist_by_score.append(node)
            self.num_calculated += 1     
            self.ablist_by_score.append((alpha, beta, None, "end",
                                        self.num_calculated, self.num_pruned))
            node.score_index = len(self.nodelist_by_score) - 1  
            if use_tt:
                from util import calc_same_boardtexts   
                
                boardtxtlist = calc_same_boardtexts(node.mb)
                _, alpha, beta = key
                for boardtxt in boardtxtlist:
                    tt[(boardtxt, alpha, beta)] = node.score            
            return node.score

        from ai import dprint
        self.calculated_by_calc_score_for_anim = False
        for node in self.nodelist:
            node.score_index = float("inf")
            node.pruned_index = float("inf")
        self.nodelist_by_score = []
        self.ablist_by_score = []
        self.num_calculated = 0
        self.num_pruned = 0
        if init_ab:
            alpha = -2 if self.shortest_victory else -1
            beta = 3 if self.shortest_victory else 1
        else:
            alpha = float("-inf")
            beta = float("inf")
        calc_ab_score(abroot, {}, alpha, beta)
        total_nodenum = self.num_pruned + self.num_calculated
        ratio = self.num_calculated / total_nodenum * 100
        dprint(debug, "ミニマックス法で計算したか", minimax)    
        dprint(debug, "計算したノードの数",  self.num_calculated)
        dprint(debug, "枝狩りしたノードの数",  self.num_pruned)
        dprint(debug, "合計",  total_nodenum)
        dprint(debug, f"割合 {ratio:.1f}%")
    
    def calc_score_for_anim(self, abroot:Node, debug:bool=False, minimax:bool=False, init_ab:bool=False, use_tt:bool=False, shortest_victory:bool|None=None):
        """評価値の計算手順の視覚化のためのデータを計算する関数

        calc_score_by_ab との違いは以下の通り
        * 置換票付き αβ 法に対応している
        * 最短の勝利を目指す評価値を計算できるようになった
        
        Args:
            abroot:
                評価値を計算するノード
            minimax:
                True の場合にミニマックス法で評価値を計算する
            init_ab:
                True の場合に α 値と β 値の初期値を評価値の最小値と最大値で初期化する
            use_tt:
                True の場合に置換表を利用する
            shortest_victory:
                最短の勝利を目指す評価値を計算するかどうかを設定する
                None の場合は self.shortest_victory の値を利用する
                それ以外の場合は self.shortest_victory の値をこの仮引数の値でこうしる
            debug:
                True の場合に評価値を計算したノードを表示する
        """    

        def assign_pruned_index(node, index):
            node.pruned_index = index
            self.num_pruned += 1
            for childnode in node.children:
                assign_pruned_index(childnode, index)
                
        def calc_node_score(node, tt, alphaorig=float("-inf"), betaorig=float("inf")):
            if minimax:
                alphaorig = float("-inf")
                betaorig = float("inf")            

            self.nodelist_by_score.append(node)
            self.ablist_by_score.append({
                "status": "start",
                "alphaorig": alphaorig,
                "betaorig": betaorig,
                "num_calculated": self.num_calculated,
                "num_pruned": self.num_pruned,
            })
            
            registered_in_tt = False
            tt_pruned = False
            if node.mb.status != Marubatsu.PLAYING:        
                self.calc_score_of_node(node)
                lower_bound = node.score
                upper_bound = node.score
            else:
                ab_updated = False
                if use_tt:
                    boardtxt = node.mb.board_to_str()
                    if boardtxt in tt:
                        registered_in_tt = True
                        lower_bound, upper_bound = tt[boardtxt]
                        if lower_bound == upper_bound:
                            node.score = lower_bound
                            tt_pruned = True
                        elif upper_bound <= alphaorig:
                            node.score = upper_bound
                            tt_pruned = True
                        elif betaorig <= lower_bound:
                            node.score = lower_bound
                            tt_pruned = True
                        else:
                            ab_updated = alphaorig < lower_bound or betaorig > upper_bound
                            alphaorig = max(alphaorig, lower_bound)
                            betaorig = min(betaorig, upper_bound)
                    else:
                        lower_bound = min_score
                        upper_bound = max_score
                    self.nodelist_by_score.append(node)
                    if tt_pruned:
                        for childnode in node.children:
                            assign_pruned_index(childnode, len(self.nodelist_by_score) - 1)  
                    self.ablist_by_score.append({
                        "status": "tt",
                        "alphaorig": alphaorig,
                        "betaorig": betaorig,
                        "tt_pruned": tt_pruned,
                        "ab_updated": ab_updated,
                        "registered_in_tt": registered_in_tt,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "num_calculated": self.num_calculated,
                        "num_pruned": self.num_pruned,
                    })
                else:
                    lower_bound = min_score
                    upper_bound = max_score
            
                if not tt_pruned:
                    alpha = alphaorig
                    beta = betaorig
                    ab_pruned = False
                    maxnode = node.mb.turn == Marubatsu.CIRCLE
                    node.score = min_score if maxnode else max_score
                    for childnode in node.children:
                        childscore = calc_node_score(childnode, tt, alpha, beta)
                        self.nodelist_by_score.append(node)
                        self.ablist_by_score.append({
                            "status": "score",
                            "alphaorig": alphaorig,
                            "betaorig": betaorig,
                            "score": node.score,
                            "childscore": childscore,
                            "registered_in_tt": registered_in_tt,
                            "lower_bound": lower_bound,
                            "upper_bound": upper_bound,
                            "num_calculated": self.num_calculated,
                            "num_pruned": self.num_pruned,
                        })   
                        if maxnode:
                            updated = node.score < childscore
                            node.score = max(node.score, childscore)
                            alpha = max(node.score, alpha)
                            if node.score >= beta:
                                ab_pruned = True
                        else:
                            updated = node.score > childscore
                            node.score = min(node.score, childscore)
                            beta = min(node.score, beta)
                            if node.score <= alpha:
                                ab_pruned = True
                        self.nodelist_by_score.append(node)
                        if ab_pruned:
                            index = node.children.index(childnode)
                            for prunednode in node.children[index + 1:]:
                                assign_pruned_index(prunednode, len(self.nodelist_by_score) - 1)
                        self.ablist_by_score.append({
                            "status": "update",
                            "alphaorig": alphaorig,
                            "betaorig": betaorig,
                            "score": node.score,
                            "registered_in_tt": registered_in_tt,
                            "updated": updated,
                            "ab_pruned": ab_pruned,
                            "lower_bound": lower_bound,
                            "upper_bound": upper_bound,
                            "num_calculated": self.num_calculated,
                            "num_pruned": self.num_pruned,
                        })   
                        if ab_pruned:
                            break 
                        
            if node.score <= alphaorig:
                score_type = "fail low"
                clower_bound = min_score
                cupper_bound = node.score
                tlower_bound = lower_bound
                tupper_bound = node.score
            elif node.score < betaorig:
                score_type = "exact value"
                clower_bound = node.score
                cupper_bound = node.score
                tlower_bound = node.score
                tupper_bound = node.score
            else:
                score_type = "fail high"
                clower_bound = node.score
                cupper_bound = max_score
                tlower_bound = node.score
                tupper_bound = upper_bound

            if use_tt:
                from util import calc_same_boardtexts
                boardtxtlist = calc_same_boardtexts(node.mb)
                for boardtxt in boardtxtlist:
                    tt[boardtxt] = (tlower_bound, tupper_bound) 

            self.nodelist_by_score.append(node)
            self.num_calculated += 1     
            self.ablist_by_score.append({
                "status": "end",
                "alphaorig": alphaorig,
                "betaorig": betaorig,
                "score": node.score,
                "registered_in_tt": registered_in_tt,
                "tt_pruned": tt_pruned,
                "score_type": score_type,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "clower_bound": clower_bound,
                "cupper_bound": cupper_bound,
                "tlower_bound": tlower_bound,
                "tupper_bound": tupper_bound,
                "num_calculated": self.num_calculated,
                "num_pruned": self.num_pruned,
            })   
            node.score_index = len(self.nodelist_by_score) - 1          
            return node.score   
                                        
        self.calculated_by_calc_score_for_anim = True
        self.minimax = minimax
        self.init_ab = init_ab
        self.use_tt = use_tt
        if shortest_victory is not None:
            self.shortest_victory = shortest_victory

        from ai import dprint       
        for node in self.nodelist:
            node.score_index = float("inf")
            node.pruned_index = float("inf")
        self.nodelist_by_score = []
        self.ablist_by_score = []
        self.num_calculated = 0
        self.num_pruned = 0
        if init_ab:
            min_score = -2 if self.shortest_victory else -1
            max_score = 3 if self.shortest_victory else 1
        else:
            min_score = float("-inf")
            max_score = float("inf")
        calc_node_score(abroot, {}, min_score, max_score)
        total_nodenum = self.num_pruned + self.num_calculated
        ratio = self.num_calculated / total_nodenum * 100
        dprint(debug, "ミニマックス法で計算したか", minimax)    
        dprint(debug, "計算したノードの数",  self.num_calculated)
        dprint(debug, "枝狩りしたノードの数",  self.num_pruned)
        dprint(debug, "合計",  total_nodenum)
        dprint(debug, f"割合 {ratio:.1f}%") 
        
    def move_bestmove_to_head(self):
        """すべてのノードの children 属性の先頭の要素を最善手を着手した要素と置き換える"""
        
        for node in self.nodelist:
            for i, childnode in enumerate(node.children):
                if node.score == childnode.score:
                    node.children[0], node.children[i] = node.children[i], node.children[0]
                    break
                     
    def move_ai_bestmove_to_head(self, ai, params={}):
        """すべてのノードの children 属性の先頭の要素を AI が計算した最善手を着手した要素と置き換える
        
        Args:
            ai:
                AI の関数
            params:
                AI に渡すパラメータ
        """
        
        for node in self.nodelist:
            if len(node.children) > 0:
                bestmove = ai(node.mb, **params)
                bestnode = node.children_by_move[bestmove]
                i = node.children.index(bestnode)
                node.children[0], node.children[i] = node.children[i], node.children[0]         
                    
    def sort_children_by_worst_score(self):
        """すべてのノードの children 属性の順番を悪い順に並べ替える
        
        具体的には、max ノードでは評価値の低い順、min ノードでは評価値の高い順に並べ替える"""

        for node in self.nodelist:
            reverse = False if node.mb.turn == Marubatsu.CIRCLE else True
            node.children.sort(key=lambda childnode: childnode.score, reverse=reverse)                    
                    
    def recalculate_score(self):
        """引き分けの局面の評価値を勝利できる可能性がある場合を考慮した評価値として再計算する"""

        for node in self.nodelist:
            if node.score == 0:
                if node.mb.move_count % 2 == 1:
                    if node.max_score > 0:
                        node.score = 0.5
                    else:
                        node.score = 0
                else:
                    if node.min_score < 0:
                        node.score = -0.5
                    else:
                        node.score = 0                    
                    
    def calc_bestmoves(self, node:Node):
        """深さ優先アルゴリズムによるゲーム木の最善手の一覧と nodelist_by_mb を計算する.
        
        Args:
            node:
                最善手の一覧を計算するノード
        """
   
        bestmoves = []
        if len(node.children) > 0:
            score_list = [childnode.score for childnode in node.children]
            if node.mb.move_count % 2 == 0:
                bestscore = max(score_list)
            else:
                bestscore = min(score_list)
            for move, childnode in node.children_by_move.items():
                if bestscore == childnode.score:
                    bestmoves.append(move)
        node.bestmoves = bestmoves

        key = tuple(node.mb.records)
        self.nodelist_by_mb[key] = node
        self.bestmoves_by_mb[key] = bestmoves

        for childnode in node.children:
            self.calc_bestmoves(childnode)                    
                    
    def calc_node_height(self, N:Node, maxdepth:int) ->float:
        """中心となるノードから特定の深さまでの部分木の、各ノードの高さを再起呼び出しで計算する.
        
        Args:
            N:
                計算するノード
            maxdepth:
                高さを計算するゲーム木の最大の深さ
        Returns:
            このノードの高さ
        """
        if len(N.children) == 0 or N.depth == maxdepth:
            N.height = 4
            return 4
        
        height = 0
        for childnode in N.children:
            height += self.calc_node_height(childnode, maxdepth)
        N.height = height
        return height        
    
    def create_subtree(self):
        """部分木を作成する.
        
        作成する部分木は、`subtree` 属性に代入された dict の下記のキーのデータを使って行う
        
        "centermb"(Marubatsu):
            中心となるノードの局面を表す Marubatsu クラスのインスタンス
            作成した中心となるノードは centernode 属性に代入される
        "selectedmb"(Marubatsu):
            選択されたノードの局面を表す Marubatsu クラスのインスタンス
            作成した選択されたノードは selectednode 属性に代入される           
        "maxdepth"(int): 
            部分木の深さの最大値               
        """
        
        bestmoves_and_score_by_board = self.subtree["bestmoves_and_score_by_board"]
        self.root = Node(Marubatsu(), bestmoves_and_score_by_board=bestmoves_and_score_by_board)
        
        depth = 0
        nodelist = [self.root]
        centermb = self.subtree["centermb"]
        centerdepth = centermb.move_count
        if centerdepth == 0:
            self.centernode = self.root
        records = centermb.records
        maxdepth = self.subtree["maxdepth"]
        while len(nodelist) > 0:
            childnodelist = []
            for node in nodelist:
                if depth < centerdepth - 1:
                    childmb = deepcopy(node.mb)
                    x, y = records[depth + 1]
                    childmb.move(x, y)
                    childnode = Node(childmb, parent=node, depth=depth+1, 
                                    bestmoves_and_score_by_board=bestmoves_and_score_by_board)   
                    node.insert(childnode)
                    childnodelist.append(childnode)
                elif depth < maxdepth:
                    node.calc_children(bestmoves_and_score_by_board=bestmoves_and_score_by_board)                   
                    if depth == centerdepth - 1:
                        for move, childnode in node.children_by_move.items():
                            if move == records[depth + 1]:
                                self.centernode = childnode
                                childnodelist.append(self.centernode)
                            else:
                                if childnode.mb.status == Marubatsu.PLAYING:
                                    childnode.children.append(None)
                    else:
                        childnodelist += node.children
                else:
                    if node.mb.status == Marubatsu.PLAYING:
                        childmb = deepcopy(node.mb)
                        board_str = node.mb.board_to_str()               
                        x, y = bestmoves_and_score_by_board[board_str]["bestmoves"][0]
                        childmb.move(x, y)
                        childnode = Node(childmb, parent=node, depth=depth+1, 
                                        bestmoves_and_score_by_board=bestmoves_and_score_by_board)   
                        node.insert(childnode)
                        childnodelist.append(childnode)
            nodelist = childnodelist
            depth += 1

        selectedmb = self.subtree["selectedmb"]
        self.selectednode = self.root
        for move in selectedmb.records[1:selectedmb.move_count+1]:
            self.selectednode = self.selectednode.children_by_move[move]
        
    def draw_subtree(self, centernode:Node|None=None, selectednode:Node|None=None, ax=None, anim_frame:int|None=None,
                     isscore:bool=False, show_bestmove:bool=False, show_score:bool=True, size:float=0.25, lw:float=0.8, maxdepth:int=2):
        """ゲーム木の部分木を描画する.
        
        Args:
            centernode:
                描画を行う部分木の中心となるノード
            selectednode:
                強調して表示する選択されたノード
            ax:
                部分木の描画を行う Axes
            anim_frame:
                Mbtree_Anim で表示する際のアニメーションのフレームを表す
                None 以外の値が代入されていた場合は、このフレーム以降のノードを暗く表示する
            isscore:
                Mbtree_Anim で何をアニメーションするかを表す
                False の場合はノードが作成された順番を表すアニメーション
                True の場合は評価値が計算されたノードの順番を表すアニメーション
            show_bestmove:
                True の場合は、最善手を着手した局面以外を暗く表示する
            show_score:
                True の場合は、評価値を表示する
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
            maxdepth:
                描画を行うゲーム木の最大の深さ
        """
        
        def calc_darkness(node):
            if show_bestmove:
                if node.parent is None:
                    return 0, show_score
                elif node.mb.last_move in node.parent.bestmoves:
                    return 0, show_score
                else:
                    return 0.2, show_score
                
            if anim_frame is None:
                return 0, show_score
            pruned_index = getattr(node, "pruned_index", None)
            if pruned_index is not None and anim_frame >= pruned_index:
                return (0.8, False)
            index = node.score_index if isscore else node.id
            return (0.5, False) if index > anim_frame else (0, isscore)
        
        self.nodes_by_rect = {}

        if centernode is None:
            centernode = self.root
        self.calc_node_height(N=centernode, maxdepth=maxdepth)
        if show_bestmove:
            width = 5 * 10
        else:
            width = 5 * (maxdepth + 1)
        height = centernode.height
        parent = centernode.parent
        if parent is not None:
            height += (len(parent.children) - 1) * 4
            parent.height = height
        if ax is None:
            fig, ax = plt.subplots(figsize=(width * size, (height + 1) * size))
            ax.set_xlim(0, width)
            ax.set_ylim(-1, height)   
            ax.invert_yaxis()
            ax.axis("off")        
        
        bottom, top = ax.get_ylim()
        top = -1
        for depth in range(1, 10, 2):
            ax.add_artist(patches.Rectangle(xy=(depth * 5 - 1, top), width=5,
                                            height=bottom - top, fc="whitesmoke"))               

        if show_bestmove:
            bestx = 5 * maxdepth + 4
            bestwidth = 50 - bestx
            ax.add_artist(patches.Rectangle(xy=(bestx, -1), width=bestwidth,
                                            height=height + 1, fc="lightgray"))
        
        nodelist = [centernode]
        depth = centernode.depth
        while len(nodelist) > 0 and depth <= maxdepth:        
            dy = 0
            if parent is not None:
                dy = parent.children.index(centernode) * 4
            childnodelist = []
            for node in nodelist:
                if node is None:
                    dy += 4
                    childnodelist.append(None)
                else:
                    dx = 5 * node.depth
                    emphasize = node is selectednode
                    darkness, show_score = calc_darkness(node)
                    rect = node.draw_node(ax=ax, maxdepth=maxdepth, emphasize=emphasize, darkness=darkness,
                                        show_score=show_score, size=size, lw=lw, dx=dx, dy=dy)
                    self.nodes_by_rect[rect] = node
                    if show_bestmove and depth == maxdepth:
                        bestnode = node
                        while len(bestnode.bestmoves) > 0:
                            bestmove = bestnode.bestmoves[0]
                            bestnode = bestnode.children_by_move[bestmove]
                            dx = 5 * bestnode.depth
                            bestnode.height = 4
                            emphasize = bestnode is selectednode
                            rect = bestnode.draw_node(ax=ax, maxdepth=bestnode.depth, emphasize=emphasize,
                                                    show_score=show_score, size=size, lw=lw, dx=dx, dy=dy)
                            self.nodes_by_rect[rect] = bestnode                                          
                        
                    dy += node.height
                    if len(node.children) > 0:  
                        childnodelist += node.children
                    else:
                        childnodelist.append(None)
            depth += 1
            nodelist = childnodelist
            
        if parent is not None:
            dy = 0
            for sibling in parent.children:
                if sibling is not centernode:
                    sibling.height = 4
                    dx = 5 * sibling.depth
                    darkness, show_score  = calc_darkness(sibling)
                    rect = sibling.draw_node(ax, maxdepth=sibling.depth, size=size, darkness=darkness,
                                            show_score=show_score, lw=lw, dx=dx, dy=dy)
                    self.nodes_by_rect[rect] = sibling
                dy += sibling.height
            dx = 5 * parent.depth
            darkness, show_score  = calc_darkness(parent)
            rect = parent.draw_node(ax, maxdepth=maxdepth, darkness=darkness, 
                                    show_score=show_score, size=size, lw=lw, dx=dx, dy=0)
            self.nodes_by_rect[rect] = parent
        
            node = parent
            while node.parent is not None:
                node = node.parent
                node.height = height
                dx = 5 * node.depth
                darkness, show_score  = calc_darkness(node)
                rect = node.draw_node(ax, maxdepth=node.depth, darkness=darkness,
                                    show_score=show_score, size=size, lw=lw, dx=dx, dy=0)
                self.nodes_by_rect[rect] = node

    def calc_and_save_bestmoves_by_board(self, path):
        """局面と最善手の対応表のデータの作成と保存

        Args:
            path:
                作成したデータを保存するファイルのパス

        Returns:
            作成したデータを返す
        """
        
        bestmoves_by_board = {}
        for node in tqdm(self.nodelist):
            txt = node.mb.board_to_str()
            if not txt in bestmoves_by_board.keys():
                bestmoves_by_board[txt] = node.bestmoves

        with gzip.open(path, "wb") as f:
            pickle.dump(bestmoves_by_board, f)
        
        return bestmoves_by_board

    def calc_and_save_bestmoves_and_score_by_board(self, path):
        """局面と最善手・評価値の対応表のデータの作成と保存

        Args:
            path:
                作成したデータを保存するファイルのパス

        Returns:
            作成したデータを返す
        """

        bestmoves_and_score_by_board = {}
        for node in tqdm(self.nodelist):
            txt = node.mb.board_to_str()
            if not txt in bestmoves_and_score_by_board.keys():
                bestmoves_and_score_by_board[txt] = {
                    "bestmoves": node.bestmoves,
                    "score": node.score,
                }

        with gzip.open(path, "wb") as f:
            pickle.dump(bestmoves_and_score_by_board, f)
        
        return bestmoves_and_score_by_board                
                    
    def save(self, fname:str):
        """ファイルへの保存
        
        Args:
            fname:
                保存するファイルのパス。ただし、拡張子は記述しないものとする
        """
        
        with gzip.open(f"{fname}.mbtree", "wb") as f:
            pickle.dump(self, f)
            print("save completed.")

    @staticmethod
    def load(fname:str):
        """ファイルへからの読み込み
        
        Args:
            fname:
                読み込むするファイルのパス。ただし、拡張子は記述しないものとする
        
        Returns:
            読み込んだ Mbtree クラスのインスタンス
        """

        with gzip.open(f"{fname}.mbtree", "rb") as f:
            return pickle.load(f)                
                       
class Mbtree_GUI(GUI):
    """Mbtree のゲーム木を描画する GUI.
    
        ←、→、↑、↓ のボタンとキーで、描画する部分木の中心となるノードを移動する
            
    Attributes:
        mbtree(Mbtree):
            描画するゲーム木を表す Mbtree クラスのインスタンス
        size(float):
            描画する画像の大きさの倍率
        width(float):
            部分木を描画する Axes の表示幅
        height(float):
            部分木を描画する Axes の高さ
        selectednode(Node):
            描画する部分木の中で選択されたノード     
    """
    
    def __init__(self, scoretable_dict:dict|None=None, show_score:bool=True, size:float=0.15):
        """イニシャライザ.
        
        Args:
            scoretable_dict:
                Dropdown に表示する局面と最善手・評価値の対応表の一覧のデータを表す dict
            show_score:
                True の場合に評価値を表示する
            size:
                描画する画像の大きさの倍率
        """
        
        if scoretable_dict is None:
            from util import load_bestmoves
            
            scoretable_dict = {
                "Standard (ai_gt7)": load_bestmoves("../data/bestmoves_and_score_by_board.dat"),
                "Shortest victory (ai_gtsv)": load_bestmoves("../data/bestmoves_and_score_by_board_shortest_victory.dat"),
                "Recalculate draw (ai_gtsvrd)": load_bestmoves("../data/bestmoves_and_score_by_board_sv_rd.dat"),
            }
        self.scoretable_dict = scoretable_dict
        self.show_score = show_score
        self.size = size
        self.width = 50
        self.height = 65
        self.selectednode = Node(Marubatsu())
        super(Mbtree_GUI, self).__init__()
        
    def create_widgets(self):
        """ウィジェットを作成する."""  

        self.output = widgets.Output()  
        self.print_helpmessage()
        self.output.layout.display = "none"
        self.left_button = self.create_button("←", 50)
        self.up_button = self.create_button("↑", 50)
        self.right_button = self.create_button("→", 50)
        self.down_button = self.create_button("↓", 50)
        self.score_button = self.create_button("評価値の表示", 100)
        self.size_slider = widgets.FloatSlider(min=0.05, max=0.25, step=0.01, description="size", value=self.size)
        self.help_button = self.create_button("？", 50)
        self.label = widgets.Label(value="", layout=widgets.Layout(width=f"50px"))
        
        with plt.ioff():
            self.fig = plt.figure(figsize=[self.width * self.size,
                                            self.height * self.size])
            self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False    
        
        self.dropdown = widgets.Dropdown(
            options=self.scoretable_dict,
            description="score table",
        )
        self.bestmoves_and_score_by_board = self.dropdown.value   
        
    def print_helpmessage(self):
        """ヘルプのメッセージを表示する"""
        
        with self.output:
            print("""操作説明

        下記のキーとボタンで中心となるノードを移動できる。
        ←、0 キー：親ノードへ移動
        ↑：一つ前の兄弟ノードへ移動
        ↓：一つ後の兄弟ノードへ移動
        →：先頭の子ノードへ移動

        テンキーで、対応するマスに着手が行われた子ノードへ移動する
        ノードの上でマウスを押すことでそのノードへ移動する
        背景が灰色になっている部分のノードは、最善手を着手し続けた場合のノードを表す
        """)
    
    def create_event_handler(self):
        """イベントハンドラを定義する."""  
        
        def on_left_button_clicked(b=None):
            if self.selectednode.parent is not None:
                self.selectednode = self.selectednode.parent
                self.update_gui()
                
        def on_right_button_clicked(b=None):
            if len(self.selectednode.children) > 0:
                self.selectednode = self.selectednode.children[0]
                self.update_gui()

        def on_up_button_clicked(b=None):
            if self.selectednode.parent is not None:
                index = self.selectednode.parent.children.index(self.selectednode)
                if index > 0:
                    self.selectednode = self.selectednode.parent.children[index - 1]
                    self.update_gui()
                
        def on_down_button_clicked(b=None):
            if self.selectednode.parent is not None:
                index = self.selectednode.parent.children.index(self.selectednode)
                if self.selectednode.parent.children[-1] is not self.selectednode:
                    self.selectednode = self.selectednode.parent.children[index + 1]
                    self.update_gui()            
                    
        def on_score_button_clicked(b=None):
            self.show_score = not self.show_score
            self.update_gui()
                    
        def on_size_slider_changed(changed):
            self.size = changed["new"]
            self.fig.set_figwidth(self.width * self.size)
            self.fig.set_figheight(self.height * self.size)
            self.update_gui()
                    
        def on_help_button_clicked(b=None):
            self.output.layout.display = "none" if self.output.layout.display is None else None
            self.update_gui()
                            
        self.left_button.on_click(on_left_button_clicked)
        self.right_button.on_click(on_right_button_clicked)
        self.up_button.on_click(on_up_button_clicked)
        self.down_button.on_click(on_down_button_clicked)
        self.score_button.on_click(on_score_button_clicked)
        self.size_slider.observe(on_size_slider_changed, names="value")
        self.help_button.on_click(on_help_button_clicked)

        def on_dropdown_changed(changed):
            self.bestmoves_and_score_by_board = self.dropdown.value
            self.update_gui()

        self.dropdown.observe(on_dropdown_changed, names="value")

        def on_key_press(event):
            keymap = {
                "left": on_left_button_clicked,
                "0": on_left_button_clicked,
                "right": on_right_button_clicked,
                "up": on_up_button_clicked,
                "down": on_down_button_clicked,
            }
            if event.key in keymap:
                keymap[event.key]()
            else:
                try:
                    num = int(event.key) - 1
                    x = num % 3
                    y = 2 - (num // 3)
                    move = (x, y)
                    if move in self.selectednode.children_by_move:
                        self.selectednode = self.selectednode.children_by_move[move]
                        self.update_gui()
                except:
                    pass            
                
        def on_mouse_down(event):
            for rect, node in self.mbtree.nodes_by_rect.items():
                if rect.is_inside(event.xdata, event.ydata):
                    self.selectednode = node
                    self.update_gui()
                    break               
                
        # fig の画像イベントハンドラを結び付ける
        self.fig.canvas.mpl_connect("key_press_event", on_key_press)
        self.fig.canvas.mpl_connect("button_press_event", on_mouse_down)
            
    def display_widgets(self):
        """ウィジェットを配置して表示する."""
        
        hbox1 = widgets.HBox([self.label, self.up_button, self.label, self.label, self.score_button])
        hbox2 = widgets.HBox([self.left_button, self.label, self.right_button,
                            self.size_slider, self.help_button])
        hbox3 = widgets.HBox([self.label, self.down_button, self.label, self.dropdown])
        self.vbox = widgets.VBox([self.output, hbox1, hbox2, hbox3, self.fig.canvas])
        display(self.vbox)  

    def update_gui(self):
        """GUI の表示を更新する."""
        
        self.ax.clear()
        self.ax.set_xlim(-1, self.width - 1)
        self.ax.set_ylim(-1, self.height - 1)   
        self.ax.invert_yaxis()
        self.ax.axis("off")   
        
        if self.selectednode.depth <= 4:
            maxdepth = self.selectednode.depth + 1
        elif self.selectednode.depth == 5:
            maxdepth = 7
        else:
            maxdepth = 9
        if self.selectednode.depth <= 6:
            centermb = self.selectednode.mb
        else:
            centermb = Marubatsu()
            for x, y in self.selectednode.mb.records[1:7]:
                centermb.move(x, y)
        self.mbtree = Mbtree(subtree={"centermb": centermb, "selectedmb": self.selectednode.mb, "maxdepth": maxdepth, 
                            "bestmoves_and_score_by_board": self.bestmoves_and_score_by_board})
        self.selectednode = self.mbtree.selectednode
        self.mbtree.draw_subtree(centernode=self.mbtree.centernode, selectednode=self.selectednode,
                                show_bestmove=True, show_score=self.show_score,
                                ax=self.ax, maxdepth=maxdepth, size=self.size)
        
        disabled = self.selectednode.parent is None
        self.set_button_status(self.left_button, disabled=disabled)
        disabled = self.selectednode.depth >= 6 or len(self.selectednode.children) == 0
        self.set_button_status(self.right_button, disabled=disabled)
        disabled = self.selectednode.parent is None or self.selectednode.parent.children.index(self.selectednode) == 0
        self.set_button_status(self.up_button, disabled=disabled)
        disabled = self.selectednode.parent is None or self.selectednode.parent.children[-1] is self.selectednode
        self.set_button_status(self.down_button, disabled=disabled)
        self.set_button_color(self.score_button, value=self.show_score)

class Mbtree_Anim(GUI):
    """Mbtree のゲーム木のアニメーションを行う GUI.
    
    ゲーム木の生成過程と、評価値の計算の過程のいずれかのアニメーションを行う
    
    Attributes:
        mbtree(Mbtree):
            描画するゲーム木を表す Mbtree クラスのインスタンス
        isscore(bool):
            False の場合はゲーム木の生成過程を表示する
            True の場合は評価値の計算の過程を表示する
        size(float):
            描画する画像の大きさの倍率
        width(float):
            部分木を描画する Axes の表示幅
        height(float):
            部分木を描画する Axes の高さ
        selectednode(Node):
            アニメーションのフレームでゲーム木に登録されたノード
        nodelist(list[Node]):
            アニメーションを行うノードの一覧
        nodenum(int):
            アニメーションを行うノードの数
    """
    def __init__(self, mbtree:Mbtree, isscore:bool=False, size:float=0.15):
        """イニシャライザ.
        
        Args:
            mbtree:
                描画するゲーム木を表す Mbtree クラスのインスタンス
            isscore:
                False の場合はゲーム木の生成過程を表示する
                True の場合は評価値の計算の過程を表示する
            size:
                描画する画像の大きさの倍率
        """

        self.mbtree = mbtree
        self.mbtree.calculated_by_calc_score_for_anim = \
                    getattr(self.mbtree, "calculated_by_calc_score_for_anim", False)
        self.isscore = isscore
        self.size = size
        self.width = 50
        self.height = 65
        self.nodelist = self.mbtree.nodelist_by_score if isscore else self.mbtree.nodelist 
        self.nodenum = len(self.nodelist)
        self.prev_frame = 0
        super(Mbtree_Anim, self).__init__()
        
    def create_widgets(self):
        """ウィジェットを作成する."""
        
        self.play = widgets.Play(max=self.nodenum - 1, interval=500)
        self.prev_button = self.create_button("<", width=30)
        self.next_button = self.create_button(">", width=30)
        self.frame_slider = widgets.IntSlider(max=self.nodenum - 1, description="frame")
        self.interval_slider = widgets.IntSlider(value=500, min=1, max=2000, description="interval")
        widgets.jslink((self.play, "value"), (self.frame_slider, "value"))    
        widgets.jslink((self.play, "interval"), (self.interval_slider, "value"))

        with plt.ioff():
            self.fig = plt.figure(figsize=[self.width * self.size,
                                            self.height * self.size])
            self.ax = self.fig.add_axes([0, 0, 1, 1])
            self.fig.canvas.toolbar_visible = False
            self.fig.canvas.header_visible = False
            self.fig.canvas.footer_visible = False
            self.fig.canvas.resizable = False 
            if self.isscore and hasattr(self.mbtree, "ablist_by_score"):
                if self.mbtree.calculated_by_calc_score_for_anim and not self.mbtree.minimax:
                    self.abfig = plt.figure(figsize=(7, 2))
                else:
                    self.abfig = plt.figure(figsize=(7, 1))
                self.abax = self.abfig.add_axes([0, 0, 1, 1])
                self.abfig.canvas.toolbar_visible = False
                self.abfig.canvas.header_visible = False
                self.abfig.canvas.footer_visible = False
                self.abfig.canvas.resizable = False 
            else:
                self.abfig = None
                
        if self.abfig is not None:
            self.node_label = widgets.Label("選択中のノード内の移動")
            self.node_first_button = self.create_button("<<", width=40)
            self.node_prev_button = self.create_button("<", width=30)
            self.node_next_button = self.create_button(">", width=30)
            self.node_last_button = self.create_button(">>", width=40)
        
    def display_widgets(self):
        """ウィジェットを配置して表示する."""
        
        hbox = widgets.HBox([self.play, self.prev_button, self.next_button, self.frame_slider, self.interval_slider])
        if self.abfig is None:
            display(widgets.VBox([hbox, self.fig.canvas])) 
        else:
            hbox2 = widgets.HBox([self.node_label, self.node_first_button, self.node_prev_button,
                                self.node_next_button, self.node_last_button])
            display(widgets.VBox([hbox, hbox2, self.abfig.canvas, self.fig.canvas])) 
        
    def create_event_handler(self):
        """イベントハンドラを登録する."""

        def on_play_changed(changed):
            self.prev_frame = changed.old
            self.update_gui()
                
        def on_prev_button_clicked(b=None):
            self.play.value -= 1
            self.update_gui()
            
        def on_next_button_clicked(b=None):
            self.play.value += 1
            self.update_gui()

        self.prev_button.on_click(on_prev_button_clicked)
        self.next_button.on_click(on_next_button_clicked)

        self.play.observe(on_play_changed, names="value")
        
        def change_frame(edge_status, diff, status_list):
            frame = self.play.value
            selectednode = self.mbtree.nodelist_by_score[frame]
            if self.mbtree.calculated_by_calc_score_for_anim:
                selectedstatus = self.mbtree.ablist_by_score[frame]["status"]
            else:
                selectedstatus = self.mbtree.ablist_by_score[frame][3]
            if selectedstatus == edge_status:
                return
            while True:
                frame += diff
                node = self.mbtree.nodelist_by_score[frame]
                if self.mbtree.calculated_by_calc_score_for_anim:
                    status = self.mbtree.ablist_by_score[frame]["status"]
                else:
                    status = self.mbtree.ablist_by_score[frame][3]
                if node == selectednode and status in status_list:
                    break
            self.play.value = frame
            self.update_gui()
                
        def on_node_first_button_clicked(b=None):
            change_frame("start", -1, ["start"])
                
        def on_node_prev_button_clicked(b=None):
            if self.mbtree.calculated_by_calc_score_for_anim:
                change_frame("start", -1, ["start", "score", "update", "tt"])
            else:
                change_frame("start", -1, ["start", "score"])

        def on_node_next_button_clicked(b=None):
            if self.mbtree.calculated_by_calc_score_for_anim:
                change_frame("end", 1, ["end", "score", "update", "tt"])
            else:
                change_frame("end", 1, ["end", "score"])
            
        def on_node_last_button_clicked(b=None):
            change_frame("end", 1, ["end"])
        
        if self.abfig is not None:
            self.node_first_button.on_click(on_node_first_button_clicked)
            self.node_prev_button.on_click(on_node_prev_button_clicked)
            self.node_next_button.on_click(on_node_next_button_clicked)
            self.node_last_button.on_click(on_node_last_button_clicked)
    
    def update_gui(self):
        """GUI の表示を更新する."""
        
        self.ax.clear()
        self.ax.set_xlim(-1, self.width - 1)
        self.ax.set_ylim(-1, self.height - 1)   
        self.ax.invert_yaxis()
        self.ax.axis("off")   
        
        self.selectednode = self.nodelist[self.play.value]
        self.centernode = self.selectednode
        if self.mbtree.algo == "bf":
            if self.centernode.depth > 0:
                self.centernode = self.centernode.parent
        while self.centernode.depth > 6:
            self.centernode = self.centernode.parent
        if self.centernode.depth <= 4:
            maxdepth = self.centernode.depth + 1
        elif self.centernode.depth == 5:
            maxdepth = 7
        else:
            maxdepth = 9
        self.mbtree.draw_subtree(centernode=self.centernode, selectednode=self.selectednode,
                                anim_frame=self.play.value, isscore=self.isscore, 
                                ax=self.ax, maxdepth=maxdepth, size=self.size)
        if self.abfig is not None:
            if self.mbtree.calculated_by_calc_score_for_anim:
                self.update_frameinfo()
                status = self.mbtree.ablist_by_score[self.play.value]["status"]
                disabled = status == "start"
                disabled2 = status == "end"
            else:
                self.update_ab()
                status = self.mbtree.ablist_by_score[self.play.value][3]
                disabled = status == "start" or status == "tt"
                disabled2 = status == "end" or status == "tt"
            self.set_button_status(self.node_first_button, disabled=disabled)
            self.set_button_status(self.node_prev_button, disabled=disabled)
            self.set_button_status(self.node_next_button, disabled=disabled2)
            self.set_button_status(self.node_last_button, disabled=disabled2)

        disabled = self.play.value == 0
        self.set_button_status(self.prev_button, disabled=disabled)
        disabled = self.play.value == self.nodenum - 1
        self.set_button_status(self.next_button, disabled=disabled)
        
    def update_ab(self):
        """calc_score_by_ab で作成したデータに対するフレームの情報の描画を更新する."""
        
        alpha, beta, score, status, num_calculated, num_pruned = self.mbtree.ablist_by_score[self.play.value]
        maxnode = self.selectednode.mb.turn == Marubatsu.CIRCLE
        acolor = "red" if maxnode else "black"
        bcolor = "black" if maxnode else "red"
                                
        self.abax.clear()
        self.abax.set_xlim(-4, 23)
        self.abax.set_ylim(-1.5, 1.5)
        self.abax.axis("off")

        minus_inf = -3
        plus_inf = 4   
        alphacoord = max(minus_inf, alpha)
        betacoord = min(plus_inf, beta)
        
        color = "lightgray" if maxnode else "aqua"
        rect = patches.Rectangle(xy=(minus_inf, -0.5), width=alphacoord-minus_inf,
                                height=1, fc=color)
        self.abax.add_patch(rect)
        rect = patches.Rectangle(xy=(alphacoord, -0.5), width=betacoord-alphacoord,
                                height=1, fc="yellow")
        self.abax.add_patch(rect)
        color = "aqua" if maxnode else "lightgray"
        rect = patches.Rectangle(xy=(betacoord, -0.5), width=plus_inf-betacoord,
                                height=1, fc=color)
        self.abax.add_patch(rect)

        self.abax.plot(range(minus_inf, plus_inf + 1), [0] * (plus_inf + 1 - minus_inf) , "|-k")
        for num in range(minus_inf, plus_inf + 1):
            if num == minus_inf:
                numtext = "-∞"
            elif num == plus_inf:
                numtext = "∞"
            else:
                numtext = num
            self.abax.text(num, -1, numtext, ha="center")
            
        arrowprops = { "arrowstyle": "->"}
        self.abax.plot(alphacoord, 0, "or")
        self.abax.annotate(f"α = {alpha}", xy=(alphacoord, 0), xytext=(minus_inf, 1),
                        arrowprops=arrowprops, ha="center", c=acolor)
        self.abax.plot(betacoord, 0, "ob")
        self.abax.annotate(f"β = {beta}", xy=(betacoord, 0), xytext=(plus_inf, 1),
                        arrowprops=arrowprops, ha="center", c=bcolor)
        if score is not None:
            self.abax.plot(score, 0, "og")
            self.abax.annotate(f"score = {score}", xy=(score, 0),
                            xytext=((minus_inf + plus_inf) / 2, 1), 
                            arrowprops=arrowprops, ha="center")
                
        facecolorlist = ["aqua", "yellow", "lightgray"]
        textcolorlist = ["black", "black", "black"]
        if maxnode:
            nodetype = f"深さ {self.selectednode.mb.move_count} max node"
            textlist = ["β 狩り (β ≦ score)", "α 値の更新 (α < score < β)", "α 値の更新なし (score ≦ α)"]
            if score is not None:
                if beta <= score:
                    textcolorlist[0] = "red"
                elif alpha < score:
                    textcolorlist[1] = "red"
                else:
                    textcolorlist[2] = "red"
        else:
            nodetype = f"深さ {self.selectednode.mb.move_count} min node"
            textlist = ["α 狩り (score <= α)", "β 値の更新 (α < score < β)", "β 値の更新なし (score ≦ β)"]
            if score is not None :
                if score <= alpha:
                    textcolorlist[0] = "red"
                elif score < beta:
                    textcolorlist[1] = "red"
                else:
                    textcolorlist[2] = "red"
                
        if status == "start":
            facecolor = "white"
            nodetype += " 処理の開始"
        elif status == "score":
            facecolor = "lightyellow"
            nodetype += " 子ノードの評価値"
        elif status == "update":
            facecolor = "lightcyan"
            if maxnode:
                nodetype += " α 値の処理"
            else:
                nodetype += " β 値の処理"
        elif status == "tt":
            textlist[0] = "置換表による置換"
            textcolorlist[0] = "red"
            facecolor = "honeydew"
        else:
            facecolor = "lavenderblush"
            nodetype += " 評価値の確定"
        self.abfig.set_facecolor(facecolor)
        self.abax.text(6, 1, nodetype)   
        for i in range(3):
            rect = patches.Rectangle(xy=(5, 0.3 - i * 0.7), width=0.8, height=0.5, fc=facecolorlist[i])
            self.abax.add_patch(rect)
            self.abax.text(6, 0.4 - i * 0.7, textlist[i], c=textcolorlist[i])    
        
        num_total = num_calculated + num_pruned
        num_ratio = num_calculated / num_total if num_total != 0 else 0
        _, _, _, _, prev_num_calculated, prev_num_pruned = self.mbtree.ablist_by_score[self.prev_frame]
        prev_num_total = prev_num_calculated + prev_num_pruned
        diff_num_calculated = num_calculated - prev_num_calculated
        diff_num_pruned = num_pruned - prev_num_pruned
        diff_num_total = num_total - prev_num_total
        diff_num_ratio = diff_num_calculated / diff_num_total if diff_num_total != 0 else 0

        textlist = [ "計算済", "枝狩り", "合計", "割合" ]
        datalist = [ num_calculated, num_pruned, num_total, f"{num_ratio * 100:.1f}%"]
        diff_datalist = [ f"{diff_num_calculated:+d}", f"{diff_num_pruned:+d}", 
                        f"{diff_num_total:+d}", f"{diff_num_ratio * 100:.1f}%"]
        for i in range(4):
            self.abax.text(15, 1 - i * 0.7, textlist[i])
            self.abax.text(19.5, 1 - i * 0.7, datalist[i], ha="right")
            self.abax.text(22.5, 1 - i * 0.7, diff_datalist[i], ha="right")

    def update_frameinfo(self):
        """calc_score_for_anim で作成したデータに対するフレームの情報の描画を更新する."""
            
        def calc_coord(score):
            return min(max(minus_inf, score), plus_inf)
            
        framedata = self.mbtree.ablist_by_score[self.play.value]
        status = framedata["status"]
        maxnode = self.selectednode.mb.turn == Marubatsu.CIRCLE
        minimax = self.mbtree.minimax
        
        self.abax.clear()
        self.abax.set_xlim(-4, 23)
        if minimax:
            self.abax.set_ylim(-1.5, 1.5)
        else:
            self.abax.set_ylim(-4.3, 2.3)
        self.abax.axis("off")

        minus_inf = -3 if self.mbtree.shortest_victory else -2
        plus_inf = 4 if self.mbtree.shortest_victory else 2

        # 範囲の色分け
        if not minimax:
            alphaorig = framedata["alphaorig"]
            betaorig = framedata["betaorig"]
            alphaorig_coord = calc_coord(alphaorig)
            betaorig_coord = calc_coord(betaorig)
            color = "lightgray" if maxnode else "aqua"
            rect = patches.Rectangle(xy=(minus_inf, -0.5), width=alphaorig_coord-minus_inf,
                                    height=1, fc=color)
            self.abax.add_patch(rect)
            rect = patches.Rectangle(xy=(alphaorig_coord, -0.5), width=betaorig_coord-alphaorig_coord,
                                    height=1, fc="yellow")
            self.abax.add_patch(rect)
            color = "aqua" if maxnode else "lightgray"
            rect = patches.Rectangle(xy=(betaorig_coord, -0.5), width=plus_inf-betaorig_coord,
                                    height=1, fc=color)
            self.abax.add_patch(rect)
        # 数直線の描画    
        self.abax.plot(range(minus_inf, plus_inf + 1), [0] * (plus_inf + 1 - minus_inf) , "|-k")
        for num in range(minus_inf, plus_inf + 1):
            if num == minus_inf:
                numtext = "" if self.mbtree.init_ab else "-∞"
            elif num == plus_inf:
                numtext = "" if self.mbtree.init_ab else "∞"
            else:
                numtext = num
            self.abax.text(num, -1, numtext, ha="center")        

        # メッセージの表示
        if minimax:
            linenum = 4
            linetop = 1
        else:
            linenum = 9
            linetop = 1.7
        textlist = [""] * linenum
        textcolorlist = ["black"] * linenum

        algorithm = "mm 法" if self.mbtree.minimax else "αβ法"
        use_tt = "〇" if self.mbtree.use_tt else "×"
        shortest_victory = "〇" if self.mbtree.shortest_victory else "×"
        init_ab = "〇" if self.mbtree.init_ab else "×"
        textlist[0] = f"{algorithm}　置換表 {use_tt}　最短 {shortest_victory}"
        if not self.mbtree.minimax:
            textlist[0] += f"　初期値 {init_ab}"
        
        textlist[1] = f"深さ {self.selectednode.mb.move_count} "
        if maxnode:
            textlist[1] += "max node"
        else:
            textlist[1] += "min node"
        
        statusdata = {
            "start": {
                "text": "処理の開始",
                "color": "white"
            },
            "tt": {
                "text": "置換表の処理",
                "color": "honeydew"
            },
            "score": {
                "text": "子ノードの評価値",
                "color": "lightyellow"
            },
            "update": {
                "text": "更新処理",
                "color": "lightcyan"
            },
            "end": {
                "text": "評価値の確定",
                "color": "lavenderblush"
            },
        }
        textlist[2] = statusdata[status]["text"]
        facecolor = statusdata[status]["color"]
        
        arrowprops = { "arrowstyle": "->"}
        leftx = -3
        rightx = 4
        centerx = (leftx + rightx) / 2
        # α 値 と β 値の初期値の表示
        if not minimax:
            if status == "start" or status == "tt":
                self.abax.plot(alphaorig_coord, 0, "or")
                self.abax.annotate(f"α = {alphaorig}", xy=(alphaorig_coord, 0),
                            xytext=(leftx, 1.7), arrowprops=arrowprops, ha="left")        
                self.abax.plot(betaorig_coord, 0, "ob")
                self.abax.annotate(f"β = {betaorig}", xy=(betaorig_coord, 0),
                            xytext=(rightx, 1.7), arrowprops=arrowprops, ha="right")        
            else:
                self.abax.text(leftx, 1.7, f"α = {alphaorig}", ha="left")   
                self.abax.text(rightx, 1.7, f"β = {betaorig}", ha="right")       
        # そのフレームでのノードの評価値の表示
        if status in ["score", "update", "end"]:
            score = framedata["score"]
            score_coord = calc_coord(score)
            text_coord = leftx if maxnode else rightx
            ha = "left" if maxnode else "right"
            self.abax.plot(score_coord, 0, "ok")
            self.abax.annotate(f"score = {score}", xy=(score_coord, 0),
                            xytext=(text_coord, 1), arrowprops=arrowprops, ha=ha)        
        # 子ノードの評価値の表示
        if status == "score":
            childscore = framedata["childscore"]
            childscore_coord = calc_coord(childscore)
            text_coord = rightx if maxnode else leftx
            ha = "right" if maxnode else "left"
            self.abax.plot(childscore_coord, 0, "og")
            self.abax.annotate(f"cscore = {childscore}", xy=(childscore_coord, 0),
                            xytext=(text_coord, 1), arrowprops=arrowprops, ha=ha)
        # 置換表にデータが登録されていたかどうかの表示
        elif status == "tt":
            if framedata["registered_in_tt"]:
                textlist[3] = "置換表に登録済"
                textcolorlist[3] = "red"
                if minimax:
                    score = framedata["lower_bound"]
                    score_coord = calc_coord(score)
                    self.abax.plot(score_coord, 0, "om")
                    self.abax.annotate(f"置換表の評価値 = {score}", xy=(score_coord, 0),
                                    xytext=(centerx, 1), arrowprops=arrowprops, ha="center")
                else:
                    if framedata["tt_pruned"]:
                        lower_bound = framedata["lower_bound"]
                        upper_bound = framedata["upper_bound"]
                        if lower_bound == upper_bound:
                            pruned_type = "exact value"
                        elif upper_bound <= alphaorig:
                            pruned_type = "fail low"
                        elif betaorig <= lower_bound:
                            pruned_type = "fail high"
                        textlist[4] = f"置換表による枝狩り ({pruned_type})"
                        textcolorlist[4] = "red"
                    else:
                        if framedata["ab_updated"]:
                            textlist[5] = "α 値または β 値の初期値の更新"
                            textcolorlist[4] = "red"            
            else:
                textlist[3] = "置換表に未登録"
        # ノードの評価値が更新されたかどうかの表示
        elif status == "update":
            if framedata["updated"]:
                textlist[3] = "評価値の更新"
                textcolorlist[3] = "red"
            else:
                textlist[3] = "評価値の更新なし"
            if not minimax:
                if score <= alphaorig:
                    score_type = "fail low"
                elif score < betaorig:
                    score_type = "exact value"
                else:
                    score_type = "fail high"
                textlist[3] += f" ({score_type})"
                if framedata["ab_pruned"]:
                    textlist[4] = "β 狩り" if maxnode else "α 狩り"
                    textcolorlist[4] = "red"
                else:
                    alpha = max(alphaorig, score) if maxnode else alphaorig
                    beta = betaorig if maxnode else min(betaorig, score)
                    alpha_coord = calc_coord(alpha)
                    beta_coord = calc_coord(beta)
                    alpha_text_coord = rightx - 1.5 if maxnode else leftx
                    beta_text_coord = rightx if maxnode else leftx + 1.5
                    ha = "right" if maxnode else "left"
                    self.abax.plot(alpha_coord, 0, "or")
                    self.abax.plot(beta_coord, 0, "ob")
                    self.abax.annotate(f"α 値", xy=(alpha_coord, 0),
                                        xytext=(alpha_text_coord, 1), arrowprops=arrowprops, ha=ha)
                    self.abax.annotate(f"β 値", xy=(beta_coord, 0),
                                        xytext=(beta_text_coord, 1), arrowprops=arrowprops, ha=ha)
        # 置換表に登録したかどうかの表示
        elif status == "end":
            if not minimax:
                score_type = framedata['score_type']
                textlist[2] += f"（{score_type}）"
            if self.mbtree.use_tt:
                if framedata["registered_in_tt"]:
                    textlist[3] = "置換表に登録されていたデータを利用"
                else:
                    textlist[3] = "置換表への登録"
                    textcolorlist[3] = "red"
                    
        def draw_bound(lower, upper, y, color):
            lower_coord = calc_coord(lower)
            upper_coord = calc_coord(upper)
            if lower == upper:
                self.abax.plot(lower_coord, y, color=color, marker="o")        
            else:
                self.abax.annotate(f"", xy=(lower_coord, y), xytext=(upper_coord, y),
                                            arrowprops={ "arrowstyle": "<->", "color": color, "linewidth": 1.5})
                
        # 下界と上界に関する表示
        if not minimax:
            lower_text = ""
            upper_text = ""
            if status != "start":
                lower_bound = framedata["lower_bound"]
                upper_bound = framedata["upper_bound"]
                if framedata["registered_in_tt"]:
                    color = "red"
                    textlist[6] = "置換表のミニマックス値の範囲"
                else:
                    color = "black"
                    textlist[6] = "ミニマックス値は置換表に未登録"
                draw_bound(lower_bound, upper_bound, -2.3, color)
                lower_text = f"下界 = {lower_bound}"
                upper_text = f"上界 = {upper_bound}"
            if status == "end" and not framedata["tt_pruned"]:
                clower_bound = framedata["clower_bound"]
                cupper_bound = framedata["cupper_bound"]
                draw_bound(clower_bound, cupper_bound, -3.0, "green")
                tlower_bound = framedata["tlower_bound"]
                tupper_bound = framedata["tupper_bound"]
                draw_bound(tlower_bound, tupper_bound, -3.7, "blue")
                textlist[7] = "計算されたミニマックス値"
                textlist[8] = "置換表に登録したミニマックス値"
                lower_text = f"下界 = {tlower_bound}"
                upper_text = f"上界 = {tupper_bound}"
            self.abax.text(leftx, -1.8, lower_text, ha="left")   
            self.abax.text(rightx, -1.8, upper_text, ha="right") 
            
        self.abfig.set_facecolor(facecolor)
        for i in range(linenum):
            self.abax.text(5, linetop - i * 0.7, textlist[i], c=textcolorlist[i])

        num_calculated = framedata["num_calculated"]
        num_pruned = framedata["num_pruned"]
        num_total = num_calculated + num_pruned
        num_ratio = num_calculated / num_total if num_total != 0 else 0
        prev_framedata = self.mbtree.ablist_by_score[self.prev_frame]
        prev_num_calculated = prev_framedata["num_calculated"]
        prev_num_pruned = prev_framedata["num_pruned"]
        prev_num_total = prev_num_calculated + prev_num_pruned
        diff_num_calculated = num_calculated - prev_num_calculated
        diff_num_pruned = num_pruned - prev_num_pruned
        diff_num_total = num_total - prev_num_total
        diff_num_ratio = diff_num_calculated / diff_num_total if diff_num_total != 0 else 0

        textlist = [ "計算済", "枝狩り", "合計", "割合" ]
        datalist = [ num_calculated, num_pruned, num_total, f"{num_ratio * 100:.1f}%"]
        diff_datalist = [ f"{diff_num_calculated:+d}", f"{diff_num_pruned:+d}", 
                        f"{diff_num_total:+d}", f"{diff_num_ratio * 100:.1f}%"]
        for i in range(4):
            self.abax.text(15, linetop - i * 0.7, textlist[i])
            self.abax.text(19.5, linetop - i * 0.7, datalist[i], ha="right")
            self.abax.text(22.5, linetop - i * 0.7, diff_datalist[i], ha="right")
            
        # 範囲の説明の表示
        if not minimax:
            facecolorlist = [
                "lightgray" if maxnode else "aqua", 
                "yellow",
                "aqua" if maxnode else "lightgray", 
            ]
            textlist = ["fail low", "exact value", "fail high"]
            textcolorlist = ["black", "black", "black"]
            if status == "tt" and framedata["tt_pruned"]:
                if pruned_type == "fail low":
                    textcolorlist[0] = "red"
                elif pruned_type == "exact value":
                    textcolorlist[1] = "red"
                elif pruned_type == "fail high":
                    textcolorlist[2] = "red"
            elif status == "update":
                if maxnode:
                    textlist[2] = "fail high (β 狩り)"
                else:
                    textlist[0] = "fail low (α 狩り)"
            if status == "update" or status == "end":
                if score_type == "fail low":
                    textcolorlist[0] = "red"
                elif score_type == "exact value":
                    textcolorlist[1] = "red"
                elif score_type == "fail high":
                    textcolorlist[2] = "red"                  
            for i in range(3):
                rect = patches.Rectangle(xy=(15, linetop - 0.1 - (i + 5) * 0.7), 
                                        width=0.8, height=0.5, fc=facecolorlist[i], ec="k")
                self.abax.add_patch(rect)
                self.abax.text(16.2, linetop - (i + 5) * 0.7, textlist[i], c=textcolorlist[i])  
               
def calc_pdist(pdistlist:list[dict], maxnode:bool=True) -> dict:
    """深さの上限を 1 とする近似値のミニマックス値の確率分布を計算する.
    
    子ノードが計算する近似値の確率分布が pdistlist の場合の
    近似値のミニマックス値の確率分布を計算して返す
    
    Attributes:
        pdistlist:
            それぞれの子ノードに対して計算される近似値の確率分布の一覧を表す list
            確率分布はキーを確率変数とし、キーの値に確率が代入されているものとする
        maxnode:
            ルートノードの種類を表す
            True の場合に max ノード、False の場合に min ノードを表す
            
    Returns:
        ルートノードの近似値のミニマックス値の確率分布を表す dict
    """
    
    pdist = defaultdict(int)
    pdistlist = [pd.items() for pd in pdistlist]
    productdata = product(*pdistlist)
    for data in productdata:
        score, prob = data[0]
        for s, p in data[1:]:
            if maxnode:
                score = max(score, s)
            else:
                score = min(score, s)
            prob *= p
        pdist[score] += prob
    return pdist
                
def calc_stval(pdist:dict) -> tuple[float, float, float]:
    """確率分布の期待値、分散、標準偏差を計算する.
    
    Attributes:
        pdist:
            確率分布を表す dict
            キーを確率変数とし、キーの値に確率が代入されているものとする
            
    Returns:
        期待値、分散、標準偏差を表す float
    """

    e = 0
    for s, p in pdist.items():
        e += s * p
    var = 0
    for s, p in pdist.items():
        var += ((s - e) ** 2) * p
    std = var ** 0.5
    return e, var, std

def draw_pdist(pdist:dict, label:str, alpha:float=1.0):
    """確率分布のグラフを描画する.
    
    Attributes:
        pdist:
            確率分布を表す dict
            キーを確率変数とし、キーの値に確率が代入されているものとする
        label:
            グラフのラベルを表す文字列
        alpha:
            グラフの透明度
    """    
    
    plt.bar(pdist.keys(), pdist.values(), width=1, label=label, alpha=alpha)
    plt.xlabel("近似値")
    plt.ylabel("確率")
    plt.legend()