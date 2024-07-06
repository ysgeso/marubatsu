from copy import deepcopy
import matplotlib.pyplot as plt
from marubatsu import Marubatsu, Marubatsu_GUI
from gui import GUI
import ipywidgets as widgets

class Node:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        mb:
            このノードの局面を表す Marubatsu クラスのインスタンス
        depth:
            このノードのゲーム木内での深さ
        height:
            このノードを描画した際の高さ
        childlen (list[Node]):
            子ノードの一覧を表す list
    """
    
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

        self.mb = mb
        self.parent = parent
        self.depth = depth
        self.children = []
        
    def insert(self, node):
        """ 子ノードを挿入する.
        
        Args:
            node(Node):
                挿入する Node クラスのインスタンス
        """

        self.children.append(node)
        
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

    def draw_node(self, ax=None, maxdepth:int|None=None, emphasize:bool=False, size:float=0.25, lw:float=0.8, dx:float=0, dy:float=0):
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
        Marubatsu_GUI.draw_board(ax, self.mb, show_result=True, emphasize=emphasize, lw=lw, dx=dx, dy=y)
        # 子ノードが存在する場合に、エッジの線と子ノードを描画する
        if len(self.children) > 0:
            if maxdepth != self.depth:   
                plt.plot([dx + 3.5, dx + 4], [y + 1.5, y + 1.5], c="k", lw=lw)
                prevy = None
                for childnode in self.children:
                    childnodey = dy + (childnode.height - 3) / 2
                    if maxdepth is None:
                        Marubatsu_GUI.draw_board(ax, childnode.mb, show_result=True, dx=dx+5, dy=childnodey, lw=lw)
                    edgey = childnodey + 1.5
                    plt.plot([dx + 4 , dx + 4.5], [edgey, edgey], c="k", lw=lw)
                    if prevy is not None:
                        plt.plot([dx + 4 , dx + 4], [prevy, edgey], c="k", lw=lw)
                    prevy = edgey
                    dy += childnode.height
            else:
                plt.plot([dx + 3.5, dx + 4.5], [y + 1.5, y + 1.5], c="k", lw=lw)

class Mbtree:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        root(Node):
            ルートノード
        nodelist_by_depth(list[list[Node]]):
            各深さのノードの list を記録する list
        nodenum:
            ゲーム木のノードの総数
    """
    
    def __init__(self):
        self.root = Node(Marubatsu())
        self.create_tree_by_bf()
        
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
        for nodelist in self.nodelist_by_depth:
            self.nodenum += len(nodelist)
        print(f"total node num = {self.nodenum}")
                    
    def calc_node_height(self, maxdepth:int):
        """ゲーム木の各ノードの高さを計算する.
        
        Args:
            maxdepth:
                高さを計算するゲーム木の最大の深さ
        """
        
        for depth in range(maxdepth, -1, -1):
            for node in self.nodelist_by_depth[depth]:
                if depth == maxdepth:
                    node.height = 4
                else:
                    node.calc_height()                  
                    
    def draw_subtree(self, centernode:Node|None=None, ax=None, size:float=0.25, lw:float=0.8, maxdepth:int=2):
        """ゲーム木の部分木を描画する.
        
        Args:
            centernode:
                描画を行う部分木の中心となるノード
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
            maxdepth:
                描画を行うゲーム木の最大の深さ
        """
        
        if centernode is None:
            centernode = self.root
        self.calc_node_height(maxdepth)
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
                    emphasize = node is centernode
                    node.draw_node(ax=ax, maxdepth=maxdepth, emphasize=emphasize, size=size, lw=lw, dx=dx, dy=dy)
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
                    sibling.draw_node(ax, maxdepth=sibling.depth, size=size, lw=lw, dx=dx, dy=dy)
                dy += sibling.height
            dx = 5 * parent.depth
            parent.draw_node(ax, maxdepth=maxdepth, size=size, lw=lw, dx=dx, dy=0)
        
            node = parent
            while node.parent is not None:
                node = node.parent
                node.height = height
                dx = 5 * node.depth
                node.draw_node(ax, maxdepth=node.depth, size=size, lw=lw, dx=dx, dy=0)
                       
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
        centernode(Node):
            描画する部分木の中心となるノード     
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
        self.centernode = self.mbtree.root
        super().__init__()
        
    def create_widgets(self):
        """ウィジェットを作成する."""  

        self.left_button = self.create_button("←", 100)
        self.up_button = self.create_button("↑", 100)
        self.right_button = self.create_button("→", 100)
        self.down_button = self.create_button("↓", 100)
        
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
            if self.centernode.parent is not None:
                self.centernode = self.centernode.parent
                self.update_gui()
                
        def on_right_button_clicked(b=None):
            if self.centernode.depth < 6 and len(self.centernode.children) > 0:
                self.centernode = self.centernode.children[0]
                self.update_gui()

        def on_up_button_clicked(b=None):
            if self.centernode.parent is not None:
                index = self.centernode.parent.children.index(self.centernode)
                if index > 0:
                    self.centernode = self.centernode.parent.children[index - 1]
                    self.update_gui()
                
        def on_down_button_clicked(b=None):
            if self.centernode.parent is not None:
                index = self.centernode.parent.children.index(self.centernode)
                if self.centernode.parent.children[-1] is not self.centernode:
                    self.centernode = self.centernode.parent.children[index + 1]
                    self.update_gui()            
                
        self.left_button.on_click(on_left_button_clicked)
        self.right_button.on_click(on_right_button_clicked)
        self.up_button.on_click(on_up_button_clicked)
        self.down_button.on_click(on_down_button_clicked)

        def on_key_press(event):
            keymap = {
                "left": on_left_button_clicked,
                "right": on_right_button_clicked,
                "up": on_up_button_clicked,
                "down": on_down_button_clicked,
            }
            if event.key in keymap:
                keymap[event.key]()
                
        # fig の画像イベントハンドラを結び付ける
        self.fig.canvas.mpl_connect("key_press_event", on_key_press)
            
    def display_widgets(self):
        """ウィジェットを配置して表示する."""
        
        hbox = widgets.HBox([self.left_button, self.right_button, self.up_button, self.down_button])
        display(widgets.VBox([hbox, self.fig.canvas]))  

    def update_gui(self):
        """GUI の表示を更新する."""
       
        self.ax.clear()
        self.ax.set_xlim(-1, self.width - 1)
        self.ax.set_ylim(0, self.height)   
        self.ax.invert_yaxis()
        self.ax.axis("off")   
        
        if self.centernode.depth <= 4:
            maxdepth = self.centernode.depth + 1
        elif self.centernode.depth == 5:
            maxdepth = 7
        else:
            maxdepth = 9
        self.mbtree.draw_subtree(self.centernode, ax=self.ax, maxdepth=maxdepth)
        
        disabled = self.centernode.parent is None
        self.set_button_status(self.left_button, disabled=disabled)
        disabled = self.centernode.depth >= 6 or len(self.centernode.children) == 0
        self.set_button_status(self.right_button, disabled=disabled)
        disabled = self.centernode.parent is None or self.centernode.parent.children.index(self.centernode) == 0
        self.set_button_status(self.up_button, disabled=disabled)
        disabled = self.centernode.parent is None or self.centernode.parent.children[-1] is self.centernode
        self.set_button_status(self.down_button, disabled=disabled)

        