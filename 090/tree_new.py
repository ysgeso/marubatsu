from copy import deepcopy
import matplotlib.pyplot as plt
from marubatsu import Marubatsu, Marubatsu_GUI

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
    
    def __init__(self, mb:Marubatsu, depth:int=0):
        """ イニシャライザ.
        
        Args:
            mb:
                このノードの局面を表す Marubatsu クラスのインスタンス
        """
        
        self.mb = mb
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
            self.insert(Node(childmb, self.depth + 1))
        
    def calc_height(self):
        """ノードを描画した際の高さを計算する."""
        
        if len(self.children) == 0:
            self.height = 4
        else:
            self.height = 0
            for childnode in self.children:
                self.height += childnode.height

    def draw_node(self, ax=None, size:float=0.25, lw:float=0.8, dx:float=0, dy:float=0):
        """ノードと子ノードの関係を描画する.
               
        Args:
            ax:
                None の場合は、Figure を作成し、このノードと子ノードの関係のみを描画する
                None でない場合は ax に、ノードの高さを考慮して描画する。そのため、
                あらかじめノードの高さを計算しておく必要がある
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
            if len(self.children) > 0:
                edgeheight = height - 4
        else:
            if len(self.children) > 0:
                edgeheight = self.height - self.children[-1].height
        
        # 自分自身のノードを (dx, dy) に描画する
        Marubatsu_GUI.draw_board(ax, self.mb, lw=lw, dx=dx, dy=dy)
        # 子ノードが存在する場合に、エッジの線と子ノードを描画する
        if len(self.children) > 0:   
            plt.plot([dx + 3.5, dx + 4, dx + 4], [dy + 1.5, dy + 1.5, dy + 1.5 + edgeheight], c="k", lw=lw)
            for childnode in self.children:
                plt.plot([dx + 4 , dx + 4.5], [dy + 1.5, dy + 1.5], c="k", lw=lw)
                dy += childnode.height

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
                    
    def draw_tree(self, startnode:Node=None, size:float=0.25, lw:float=0.8, maxdepth:int=2):
        """ゲーム木の部分木を描画する.
        
        Args:
            startnode:
                描画を行う部分木のルートノード
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
            maxdepth:
                描画を行うゲーム木の最大の深さ
        """
        
        if startnode is None:
            startnode = self.root
        self.calc_node_height(maxdepth)
        width = 5 * (maxdepth - startnode.depth + 1)
        height = startnode.height
        fig, ax = plt.subplots(figsize=(width * size, height * size))
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)   
        ax.invert_yaxis()
        ax.axis("off")        
        
        nodelist = [startnode]
        depth = startnode.depth
        dx = 0
        while len(nodelist) > 0 and depth <= maxdepth:        
            dy = 0
            childnodelist = []
            for node in nodelist:
                if node is None:
                    dy += 4
                    childnodelist.append(None)
                else:
                    node.draw_node(ax=ax, size=size, lw=lw, dx=dx, dy=dy)
                    dy += node.height
                    if len(node.children) > 0:  
                        childnodelist += node.children
                    else:
                        childnodelist.append(None)
            dx += 5
            depth += 1
            nodelist = childnodelist