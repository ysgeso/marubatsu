from copy import deepcopy
import matplotlib.pyplot as plt
from marubatsu import Marubatsu_GUI

class Node:
    """ 〇×ゲームのゲーム木のノード.

    Attributes:
        mb:
            このノードの局面を表す Marubatsu クラスのインスタンス
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

    def draw_node(self, size:float=0.25, lw:float=0.8):
        """ノードと子ノードの関係を描画する.
               
        Args:
            size:
                描画する画像の倍率
            lw:
                描画する図形の線の太さ
        """            
        
        width = 8
        height = len(self.children) * 4
        fig, ax = plt.subplots(figsize=(width * size, height * size))
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)   
        ax.invert_yaxis()
        ax.axis("off")
        
        # 自分自身のノードを (0, 0) に描画する
        Marubatsu_GUI.draw_board(ax, self.mb, lw=lw)
        plt.plot([3.5, 4, 4], [1.5, 1.5, 1.5 + height - 4], c="k", lw=lw)
        # i 番の子ノードを (5, i * 4) に描画する
        for i, childnode in enumerate(self.children):
            Marubatsu_GUI.draw_board(ax, childnode.mb, dx=5, dy=i*4, lw=lw)
            plt.plot([4 , 4.5], [1.5 + i * 4, 1.5 + i * 4], c="k", lw=lw)
