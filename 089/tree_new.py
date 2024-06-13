from copy import deepcopy
import matplotlib.pyplot as plt
from marubatsu import Marubatsu_GUI

class Node:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        mb:
            このノードの局面を表す Marubatsu クラスのインスタンス
        height:
            このノードを描画した際の高さ
        childlen (list[Node]):
            子ノードの一覧を表す list
    """
    
    def __init__(self, mb):
        """ イニシャライザ.
        
        Args:
            mb:
                このノードの局面を表す Marubatsu クラスのインスタンス
        """
        
        self.mb = mb
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
            self.insert(Node(childmb))

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
                Marubatsu_GUI.draw_board(ax, childnode.mb, dx=dx+5, dy=dy, lw=lw)
                plt.plot([dx + 4 , dx + 4.5], [dy + 1.5, dy + 1.5], c="k", lw=lw)
                dy += childnode.height

class Mbtree:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        root(Node):
            ルートノード
    """
    
    def __init__(self):
        self.root = Node(Marubatsu())
        self.create_tree_by_bf()
        
    def create_tree_by_bf(self):
        """幅優先アルゴリズムによるゲーム木の作成."""
        
        # 深さ 1 のノードの作成
        self.root.calc_children()
        # 深さ 2 のノードの作成
        for childnode in self.root.children:
            childnode.calc_children()
            # 深さ 3 のノードの作成
            for grandchildnode in childnode.children:
                grandchildnode.calc_children()
                # 深さ 4 のノードの作成
                for greatgrandchildnode in grandchildnode.children:
                    greatgrandchildnode.calc_children()
                    
    def calc_node_height(self):
        """ゲーム木の各ノードの高さを計算する."""
        
        for childnode in self.root.children:
            # 深さ 2 のノードの高さの計算
            for grandchildnode in childnode.children:
                grandchildnode.calc_height()
            # 深さ 1 のノードの高さの計算
            childnode.calc_height()
        # 深さ 0 のノードの高さの計算
        self.root.calc_height()                    
                    
    def draw_tree(self, size=0.25, lw=0.8):
        """ゲーム木を描画する.
        
        Args:
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
        """
        
        self.calc_node_height()   
        width = 13
        height = self.root.height
        fig, ax = plt.subplots(figsize=(width * size, height * size))
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)   
        ax.invert_yaxis()
        ax.axis("off")        
            
        # 深さ 0 のノードの描画
        self.root.draw_node(ax=ax, size=size, lw=lw)
        dy = 0
        # 深さ 1 のノードの描画
        for childnode in self.root.children:
            childnode.draw_node(ax=ax, size=size, lw=lw, dx=5, dy=dy)
            dy += childnode.height