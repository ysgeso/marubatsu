from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from marubatsu import Marubatsu, Marubatsu_GUI
from gui import GUI
import ipywidgets as widgets
import gzip
import pickle

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
    """
    
    # ノードを作成した回数を表すクラス属性
    count = 0
    
    def __init__(self, mb:Marubatsu, parent=None, depth:int=0):
        """ イニシャライザ.
        
        Args:
            mb:
                このノードの局面を表す Marubatsu クラスのインスタンス
            parent:
                親ノード。None の場合は親ノードが存在しないことを意味する
            depth:
                深さ
        """

        self.id = Node.count
        Node.count += 1
        self.mb = mb
        self.parent = parent
        self.depth = depth
        self.children = []
        self.children_by_move = {}         
        
    def insert(self, node):
        """ 子ノードを挿入する.
        
        Args:
            node(Node):
                挿入する Node クラスのインスタンス
        """

        self.children.append(node)
        self.children_by_move[node.mb.last_move] = node
        
    def calc_children(self):
        """子ノードを計算する"""
        
        self.children = []
        for x, y in self.mb.calc_legal_moves():
            childmb = deepcopy(self.mb)
            childmb.move(x, y)
            self.insert(Node(childmb, parent=self, depth=self.depth + 1))
        
    def calc_height(self):
        """ノードを描画した際の高さを計算する."""
        
        if len(self.children) == 0:
            self.height = 4
        else:
            self.height = 0
            for childnode in self.children:
                self.height += childnode.height

    def draw_node(self, ax=None, maxdepth:int|None=None, emphasize:bool=False, size:float=0.25, lw:float=0.8, dx:float=0, dy:float=0) -> Rect:
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
        Marubatsu_GUI.draw_board(ax, self.mb, show_result=True, 
                                score=getattr(self, "score", None), emphasize=emphasize, lw=lw, dx=dx, dy=y)
        rect = Rect(dx, y, 3, 3)
        # 子ノードが存在する場合に、エッジの線と子ノードを描画する
        if len(self.children) > 0:
            if maxdepth != self.depth:   
                plt.plot([dx + 3.5, dx + 4], [y + 1.5, y + 1.5], c="k", lw=lw)
                prevy = None
                for childnode in self.children:
                    childnodey = dy + (childnode.height - 3) / 2
                    if maxdepth is None:
                        Marubatsu_GUI.draw_board(ax, childnode.mb, show_result=True,
                                                score=getattr(childnode, "score", None), dx=dx+5, dy=childnodey, lw=lw)
                    edgey = childnodey + 1.5
                    plt.plot([dx + 4 , dx + 4.5], [edgey, edgey], c="k", lw=lw)
                    if prevy is not None:
                        plt.plot([dx + 4 , dx + 4], [prevy, edgey], c="k", lw=lw)
                    prevy = edgey
                    dy += childnode.height
            else:
                plt.plot([dx + 3.5, dx + 4.5], [y + 1.5, y + 1.5], c="k", lw=lw)
                
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
        nodelist_by_mb(dict[tuple])
            Marubatsu クラスの棋譜を表す records 属性をキーとし、
            キーの値に対応するノードを代入する dict
        bestmoves_by_mb(dict[tuple])
            Marubatsu クラスの棋譜を表す records 属性をキーとし、
            キーの値に対応するノードの最善手の一覧を代入する dict
    """
    
    def __init__(self, algo:str="bf"):
        """イニシャライザ.
        
        Args:
            algo:
                ゲーム木を生成するアルゴリズムを表す文字列
                "bf" の場合は幅優先アルゴリズムで生成する
                それ以外の場合は深さ優先アルゴリズムで生成する        
        """
        
        self.algo = algo
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

    def calc_score_by_bf(self):
        """深さ優先アルゴリズムによるゲーム木の評価値の計算."""        
        
        self.nodelist_by_score = self.nodelist[:]
        for nodelist in reversed(self.nodelist_by_depth):
            for node in nodelist:
                if node.mb.status == Marubatsu.CIRCLE:
                    node.score = 1
                elif node.mb.status == Marubatsu.DRAW:
                    node.score = 0
                elif node.mb.status == Marubatsu.CROSS:
                    node.score = -1
                else:
                    score_list = [childnode.score for childnode in node.children]
                    if node.mb.move_count % 2 == 0:
                        score = max(score_list)
                    else:
                        score = min(score_list)
                    node.score = score
                self.nodelist_by_score.append(node)
                node.score_index = len(self.nodelist_by_score) - 1    
                
    def calc_score_by_df(self, node:Node) -> float:
        """深さ優先アルゴリズムによるゲーム木の評価値の計算.
        
        Args:
            node:
                評価値を計算するノード
        
        Returns:
            このノードの評価値
        """
                
        self.nodelist_by_score.append(node)
        if node.mb.status == Marubatsu.CIRCLE:
            node.score = 1
        elif node.mb.status == Marubatsu.DRAW:
            node.score = 0
        elif node.mb.status == Marubatsu.CROSS:
            node.score = -1
        else:
            score_list = []
            for childnode in node.children:
                score_list.append(self.calc_score_by_df(childnode))
                self.nodelist_by_score.append(node)
            if node.mb.move_count % 2 == 0:
                score = max(score_list)
            else:
                score = min(score_list)
            node.score = score
            
        self.nodelist_by_score.append(node)
        node.score_index = len(self.nodelist_by_score) - 1        
        return node.score                
                    
    def calc_bestmoves(self, node:Node):
        """深さ優先アルゴリズムによるゲーム木の最善手の一覧と nodelist_by_mb を計算する.
        
        Args:
            node:
                最善手の一覧を計算するノード
        """
        bestmoves = []
        for move, childnode in node.children_by_move.items():
            if node.score == childnode.score:
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
            
                    
    def draw_subtree(self, centernode:Node|None=None, selectednode:Node|None=None, ax=None, size:float=0.25, lw:float=0.8, maxdepth:int=2):
        """ゲーム木の部分木を描画する.
        
        Args:
            centernode:
                描画を行う部分木の中心となるノード
            selectednode:
                強調して表示する選択されたノード
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
            maxdepth:
                描画を行うゲーム木の最大の深さ
        """
        
        self.nodes_by_rect = {}

        if centernode is None:
            centernode = self.root
        self.calc_node_height(N=centernode, maxdepth=maxdepth)
        width = 5 * (maxdepth + 1)
        height = centernode.height
        parent = centernode.parent
        if parent is not None:
            height += (len(parent.children) - 1) * 4
            parent.height = height
        if ax is None:
            fig, ax = plt.subplots(figsize=(width * size, height * size))
            ax.set_xlim(0, width)
            ax.set_ylim(0, height)   
            ax.invert_yaxis()
            ax.axis("off")        
        
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
                    rect = node.draw_node(ax=ax, maxdepth=maxdepth, emphasize=emphasize, size=size, lw=lw, dx=dx, dy=dy)
                    self.nodes_by_rect[rect] = node
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
                    rect = sibling.draw_node(ax, maxdepth=sibling.depth, size=size, lw=lw, dx=dx, dy=dy)
                    self.nodes_by_rect[rect] = sibling
                dy += sibling.height
            dx = 5 * parent.depth
            rect = parent.draw_node(ax, maxdepth=maxdepth, size=size, lw=lw, dx=dx, dy=0)
            self.nodes_by_rect[rect] = parent
        
            node = parent
            while node.parent is not None:
                node = node.parent
                node.height = height
                dx = 5 * node.depth
                rect = node.draw_node(ax, maxdepth=node.depth, size=size, lw=lw, dx=dx, dy=0)
                self.nodes_by_rect[rect] = node
                    
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
    
    def __init__(self, mbtree:Mbtree, size:float=0.15):
        """イニシャライザ.
        
        Args:
            mbtree:
                描画するゲーム木を表す Mbtree クラスのインスタンス
            size(float):
                描画する画像の大きさの倍率
        """
        
        self.mbtree = mbtree
        self.size = size
        self.width = 50
        self.height = 64
        self.selectednode = self.mbtree.root
        super().__init__()
        
    def create_widgets(self):
        """ウィジェットを作成する."""  

        self.output = widgets.Output()  
        self.left_button = self.create_button("←", 50)
        self.up_button = self.create_button("↑", 50)
        self.right_button = self.create_button("→", 50)
        self.down_button = self.create_button("↓", 50)
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
                    
        def on_help_button_clicked(b=None):
            self.output.clear_output()
            with self.output:
                print("""操作説明

    下記のキーとボタンで中心となるノードを移動できる。
    ←、0 キー：親ノードへ移動
    ↑：一つ前の兄弟ノードへ移動
    ↓：一つ後の兄弟ノードへ移動
    →：先頭の子ノードへ移動

    テンキーで、対応するマスに着手が行われた子ノードへ移動する
    ノードの上でマウスを押すことでそのノードへ移動する
    """)
                            
        self.left_button.on_click(on_left_button_clicked)
        self.right_button.on_click(on_right_button_clicked)
        self.up_button.on_click(on_up_button_clicked)
        self.down_button.on_click(on_down_button_clicked)
        self.help_button.on_click(on_help_button_clicked)

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
        
        hbox1 = widgets.HBox([self.label, self.up_button, self.label])
        hbox2 = widgets.HBox([self.left_button, self.label, self.right_button,
                            self.label, self.help_button])
        hbox3 = widgets.HBox([self.label, self.down_button, self.label])
        display(widgets.VBox([self.output, hbox1, hbox2, hbox3, self.fig.canvas]))   

    def update_gui(self):
        """GUI の表示を更新する."""
       
        self.ax.clear()
        self.ax.set_xlim(-1, self.width - 1)
        self.ax.set_ylim(0, self.height)   
        self.ax.invert_yaxis()
        self.ax.axis("off")   
        
        if self.selectednode.depth <= 4:
            maxdepth = self.selectednode.depth + 1
        elif self.selectednode.depth == 5:
            maxdepth = 7
        else:
            maxdepth = 9
        centernode = self.selectednode
        while centernode.depth > 6:
            centernode = centernode.parent
        self.mbtree.draw_subtree(centernode=centernode, selectednode=self.selectednode, ax=self.ax, maxdepth=maxdepth)
        
        disabled = self.selectednode.parent is None
        self.set_button_status(self.left_button, disabled=disabled)
        disabled = self.selectednode.depth >= 6 or len(self.selectednode.children) == 0
        self.set_button_status(self.right_button, disabled=disabled)
        disabled = self.selectednode.parent is None or self.selectednode.parent.children.index(self.selectednode) == 0
        self.set_button_status(self.up_button, disabled=disabled)
        disabled = self.selectednode.parent is None or self.selectednode.parent.children[-1] is self.selectednode
        self.set_button_status(self.down_button, disabled=disabled)

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
        self.mbtree = mbtree
        self.isscore = isscore
        self.size = size
        self.width = 50
        self.height = 64
        self.nodelist = self.mbtree.nodelist_by_score if isscore else self.mbtree.nodelist 
        self.nodenum = len(self.nodelist)
        super().__init__()
        
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
        
    def display_widgets(self):
        """ウィジェットを配置して表示する."""
        
        hbox = widgets.HBox([self.play, self.prev_button, self.next_button, self.frame_slider, self.interval_slider])
        display(widgets.VBox([hbox, self.fig.canvas])) 
        
    def create_event_handler(self):
        """イベントハンドラを登録する."""

        def on_play_changed(changed):
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
    
    def update_gui(self):
        """GUI の表示を更新する."""
        
        self.ax.clear()
        self.ax.set_xlim(-1, self.width - 1)
        self.ax.set_ylim(0, self.height)   
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
                                ax=self.ax, maxdepth=maxdepth)
        for rect, node in self.mbtree.nodes_by_rect.items():
            index = node.score_index if self.isscore else node.id
            if index > self.play.value:
                self.ax.add_artist(patches.Rectangle(xy=(rect.x, rect.y), width=rect.width,
                                                        height=rect.height, fc="black", alpha=0.5))
            if node is self.selectednode:
                self.ax.add_artist(patches.Rectangle(xy=(rect.x, rect.y), width=rect.width,
                                                        height=rect.height, ec="red", fill=False, lw=2))

        disabled = self.play.value == 0
        self.set_button_status(self.prev_button, disabled=disabled)
        disabled = self.play.value == self.nodenum - 1
        self.set_button_status(self.next_button, disabled=disabled)