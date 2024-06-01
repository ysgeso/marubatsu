# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from collections import defaultdict
from typing import NamedTuple
import random
import matplotlib as mlp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import japanize_matplotlib
import math
import ipywidgets as widgets
from copy import deepcopy

class Markpat(NamedTuple):   
    """マークのパターン.
    
    Attributes:
        last_turn (int):
            直前のターンのマークの数
        turn (int):
            現在のターンのマークの数
        empty (int):
            空のマスの数
    """
    
    last_turn: int
    turn: int
    empty: int

class Marubatsu:
    """ 〇×ゲーム.

    Attributes:
        クラス属性
        EMPTY (str):
            空のマスを表す文字列
        CIRCLE (str):
            〇 のマークを表す文字列
        CROSS (str):
            × のマークを表す文字列
        DRAW (str):
            引き分けを表す文字列
        PLAYING (str):
            決着がついていないことを表す文字列
        
        インスタンス属性
        BOARD_SIZE (int):
            ゲーム盤の縦横のサイズを表す数値
        board (list[list[str]):
            ゲーム盤を表す 2 次元配列の list
            2 つのインデックスは、順に x 座標、y 座標を表す
            空白のマスは " "、〇 のマスは "o"、× のマスは "x" を代入する
        move_count (int):
            着手を行った回数
        status (str):
            ゲームの状態
            CIRCLE、CROSS、DRAW、PLAYING のいずれかの状態が代入される
        last_move (tuple(int, int)):
            直前の着手の座標
        last_turn (str):
            直前の手番
        records: (list[tuple[int, int]])
            ゲームの棋譜
        board_records: (list[list[list[str]])
            各手数のゲーム盤のデータ
    """

    EMPTY = "."
    CIRCLE = "o"
    CROSS = "x"
    DRAW = "draw"
    PLAYING = "playing"
    
    def __init__(self, board_size: int=3):
        """ イニシャライザ 
        
        Args:
            board_size:
                ゲーム盤の縦横のサイズ。デフォルト値は 3
        """

        # ゲーム盤の縦横のサイズ
        self.BOARD_SIZE = board_size
        # 〇×ゲーム盤を再起動するメソッドを呼び出す
        self.restart()

    def initialize_board(self):
        """ ゲーム盤のデータの初期化. """

        self.board = [[Marubatsu.EMPTY] * self.BOARD_SIZE for y in range(self.BOARD_SIZE)]

    def place_mark(self, x: int, y: int, mark: str) -> bool:
        """ ゲーム盤の指定したマスに指定したマークを配置する.

        (x, y) のマスに mark で指定したマークを配置する.
        (x, y) のマスがゲーム盤の範囲外の場合は、メッセージを表示する.
        (x, y) のマスに既にマークが配置済の場合は、メッセージを表示する.
        返り値として配置できたかどうかを表す論理型のデータを返す.

        Args:
            x:
                マークを配置するマスの x 座標
            y:
                マークを配置するマスの y 座標
            mark:
                配置するマークを表す文字列
                
        Returns:
            マークを配置できた場合は True、配置できなかった場合は False
        """

        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            if self.board[x][y] == Marubatsu.EMPTY:
                self.board[x][y] = mark
                return True
            else:
                print("(", x, ",", y, ") のマスにはマークが配置済です")
                return False
        else:
            print("(", x, ",", y, ") はゲーム盤の範囲外の座標です")
            return False   
            
    def restart(self):
        """ 〇×ゲームを再起動する. """

        self.initialize_board()
        self.turn = Marubatsu.CIRCLE     
        self.move_count = 0
        self.status = Marubatsu.PLAYING
        self.last_move = -1, -1          
        self.last_turn = None
        self.records = [self.last_turn]
    
    def move(self, x: int, y: int):
        """ ゲーム盤の指定したマスに着手する.

        Args:
            x:
                マークを配置するマスの x 座標
            y:
                マークを配置するマスの y 座標
        """

        if self.place_mark(x, y, self.turn):
            self.last_turn = self.turn
            self.turn = Marubatsu.CROSS if self.turn == Marubatsu.CIRCLE else Marubatsu.CIRCLE  
            self.move_count += 1
            self.status = self.judge()
            self.last_move = x, y
            if len(self.records) <= self.move_count:            
                self.records.append(self.last_move)
            else:
                self.records[self.move_count] = self.last_move
                self.records = self.records[0:self.move_count + 1]   
                            
    def change_step(self, step:int):
        """step 手目の局面に移動する.
        
        Args:
            step:
                移動する局面の手数
        """
        # step の範囲を正しい範囲に修正する
        step = max(0, min(len(self.records) - 1, step))
        records = self.records
        self.restart()
        for x, y in records[1:step+1]:
            self.move(x, y)
        self.records = records

    def judge(self) -> str:
        """ 勝敗判定.
        
        Returns:
            以下のいずれかの値を返す
            Marubatsu.CIRCLE:  〇 の勝利
            Marubatsu.CROSS:   × の勝利
            Marubatsu.DRAW:    引き分け
            Marubatsu.PLAYING: 決着がついていない
        """
        
        # 〇 の勝利の判定
        if self.is_winner(Marubatsu.CIRCLE):
            return Marubatsu.CIRCLE
        # × の勝利の判定
        elif self.is_winner(Marubatsu.CROSS):
            return Marubatsu.CROSS   
        # 引き分けの判定
        elif self.is_full():
            return Marubatsu.DRAW
        # 上記のどれでもなければ決着がついていない
        else:
            return Marubatsu.PLAYING            
            
    def __str__(self):
        # ゲームの決着がついていない場合は、手番を表示する
        if self.status == Marubatsu.PLAYING:
            text = "Turn " + self.turn + "\n"
        # 決着がついていれば勝者を表示する
        else:
            text = "winner " + self.status + "\n"
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                lastx, lasty = self.last_move
                if x == lastx and y == lasty:
                    text += self.board[x][y].upper()
                else:
                    text += self.board[x][y]
            text += "\n"
        return text
    
    def is_winner(self, player:str) -> bool:
        """player のプレイヤーの勝利判定.

        Args:
            player: 
                判定するプレイヤーを表す文字列
                Marubatsu.CIRCLE または Marubatsu.CROSS を指定する

        Returns:
            player のプレイヤーが勝利している場合は True
            そうでない場合は False
        """
        
        # 横方向と縦方向の判定
        for i in range(self.BOARD_SIZE):
            if self.is_same(player, coord=[0, i], dx=1, dy=0) or \
            self.is_same(player, coord=[i, 0], dx=0, dy=1):
                return True
        # 左上から右下方向の判定
        if self.is_same(player, coord=[0, 0], dx=1, dy=1):
            return True
        # 右上から左下方向の判定
        if self.is_same(player, coord=[self.BOARD_SIZE - 1, 0], dx=-1, dy=1):
            return True

        # どの一直線上にも配置されていない場合は、player は勝利していないので False を返す
        return False
   
    def is_same(self, mark:str, coord:list[int], dx:int, dy:int) -> bool:
        """指定したマスにマークが配置されているかの判定.
        
        coord のマスから、dx, dy 方向に存在するマスに、
        mark のマークが配置されているかどうかを判定する

        Args:
            mark: 判定するマークを表す文字列
                Marubatsu.CIRCLE または Marubatsu.CROSS を指定する
            coord:
                最初のマスの xy 座標を表す list
            dx:
                次のマスの x 座標の差分
            dy:
                次のマスの y 座標の差分

        Returns:
            すべてのマスに mark のマークが配置されている場合は True
            そうでない場合は False
        """
        
        x, y = coord
        text_list = [self.board[x + i * dx][y + i * dy] 
                     for i in range(self.BOARD_SIZE)]
        line_text = "".join(text_list)
        return line_text == mark * self.BOARD_SIZE

    def is_full(self) -> bool:
        """すべてのマスが埋まっているかどうかの判定.        

        Returns:
            すべてのマスが埋まっている場合は True
            そうでない場合は False
        """
        
        return self.move_count == self.BOARD_SIZE ** 2

    def play(self, ai:list, ai_dict:dict|None=None, params:list[dict]|None=None, verbose:bool=True, seed:bool|None=None, gui:bool=False, size:float=3) -> str | None:
        """〇×ゲームをプレイする.
        
        仮引数 ai でそれぞれの手番の着手を誰が担当するかを指定する
        ゲーム盤が表示されるので、テキストボックスに着手を行う座標を入力する
        座標は x,y の形式で入力する
        返り値として、勝者を表す文字列を返す
        
        Args:
            ai: それぞれの手番を誰が担当するかを指定する list
                0 番の要素が 〇 の手番、1 番の要素が × の手番を表す
                要素に None が代入されている場合は人間が担当することを表す
                要素に関数が代入されている場合は、その関数によって AI が着手を行う
                
                AI の処理を行う関数の仮引数は Marubatsu クラスのインスタンスで、
                着手を行う座標を表す (x, y) の形式の tuple を返すものとする
            ai_dict:
                gui=True の場合に、Dropdown で選択できる AI の一覧を表す dict
            params:
                それぞれの AI に渡すパラメータを要素として持つ list
                パラメータは、マッピング型の展開で AI に渡す
            verbose:
                途中経過を表示するかどうか
                True の場合は途中経過を表示し、False の場合は途中経過を表示しない
            seed:
                None でない場合は、乱数の種をこの値で設定する
                None の場合はなにもしない
            gui:
                False の場合は、入出力を CUI（文字列）で行う
                True の場合は、入出力を GUI（画像）で行う
            size:
                gui が True の場合に描画するゲーム盤の画像のサイズ
                
        Returns:
            gui が True の場合で決着がついていない場合は None
            決着がついた場合または、gui が False の場合は勝者を表す下記のいずれかの文字列
                Marubatsu.CIRCLE: 〇 の勝利
                Marubatsu.CROSS:  × の勝利
                Marubatsu.DRAW:   引き分け
        """
       
        # params が None の場合のデフォルト値を設定する
        if params is None:
            params = [{}, {}]
            
        # 一部の仮引数をインスタンスの属性に代入する
        self.ai = ai
        self.params = params
        self.verbose = verbose
        self.gui = gui
        
        # seed が None でない場合は、seed を乱数の種として設定する
        if seed is not None:
            random.seed(seed)

        # gui が True の場合に、GUI の処理を行う Marubatsu_GUI のインスタンスを作成する
        if gui:
            mb_gui = Marubatsu_GUI(self, ai_dict=ai_dict, size=size)  
        else:
            mb_gui = None
            
        self.restart()
        return self.play_loop(mb_gui)
    
    def play_loop(self, mb_gui:Marubatsu_GUI|None) -> str | None:
        """〇×ゲームのゲーム開始後の繰り返し処理を行う.
        
        Args:
            mb_gui:
                GUI の場合は Marubatsu_GUI クラスのインスタンス
                CUI の場合は None
        
        Returns:
            決着がついた場合は勝者を表す文字列
            決着がついていない場合は None
        """
        
        ai = self.ai
        params = self.params
        verbose = self.verbose
        gui = self.gui
        
        # ゲームの決着がついていない間繰り返す
        while self.status == Marubatsu.PLAYING:
            # 現在の手番を表す ai のインデックスを計算する
            index = 0 if self.turn == Marubatsu.CIRCLE else 1
            # ゲーム盤の表示
            if verbose:
                if gui:
                    # AI どうしの対戦の場合は画面を描画しない
                    if ai[0] is None or ai[1] is None:
                        mb_gui.draw_board()
                    # 手番を人間が担当する場合は、play メソッドを終了する
                    if ai[index] is None:
                        return
                else:
                    print(self)
                    
            # ai が着手を行うかどうかを判定する
            if ai[index] is not None:
                x, y = ai[index](self, **params[index])
            else:
                # キーボードからの座標の入力
                coord = input("x,y の形式で座標を入力して下さい。exit を入力すると終了します")
                # "exit" が入力されていればメッセージを表示して関数を終了する
                if coord == "exit":
                    print("ゲームを終了します")
                    return       
                # x 座標と y 座標を要素として持つ list を計算する
                xylist = coord.split(",")
                # xylist の要素の数が 2 ではない場合
                if len(xylist) != 2:
                    # エラーメッセージを表示する
                    print("x, y の形式ではありません")
                    # 残りの while 文のブロックを実行せずに、次の繰り返し処理を行う
                    continue
                x, y = xylist
            # (x, y) に着手を行う
            try:
                self.move(int(x), int(y))
            except:
                print("整数の座標を入力して下さい")

        # 決着がついたので、ゲーム盤を表示する
        if verbose:
            if gui:
                mb_gui.draw_board()
            else:
                print(self)
                
        return self.status
    
    def calc_legal_moves(self) -> list[tuple[int, int]]:
        """合法手の一覧を表す list を計算する.

        Returns:
            合法手の一覧を要素として持つ list
            合法手は座標を表す (x, y) の形式の tuple
        """
        
        legal_moves = [(x, y) for y in range(self.BOARD_SIZE) 
                            for x in range(self.BOARD_SIZE)
                            if self.board[x][y] == Marubatsu.EMPTY]
        return legal_moves
    
    def count_marks(self, coord:list[int], dx:int, dy:int, datatype:str="dict") -> defaultdict | tuple[int, int, int]:
        """指定したマスに配置されている 〇 と × と空のマスの数を数える.
        
        coord のマスから、dx, dy 方向に存在するマスに、
        〇 と × と空のマスの数がそれぞれいくつあるかを数える
        返り値のデータ型を、datatype の値によって、dict と tuple の中から選択できる

        Args:
            coord:
                最初のマスの xy 座標を表す list
            dx:
                次のマスの x 座標の差分
            dy:
                次のマスの y 座標の差分
            datatype:
                "dict"（デフォルト値）の場合に返り値として dict を返す
                それ以外の場合は返り値として tuple を返す

        Returns:
            datatype が "dict" の場合:
                Marubatsu.CIRCLE、Marubatsu.CROSS、Marubatsu.EMPTY をキーとする defaultdict
                それぞれのキーの値は、キーが示すものが配置されているマスの数を表す
            それ以外の場合
                (直前の手番のマークの数、現在の手番のマークの数、空のマスの数) を要素とする tuple
        """    
        
        x, y = coord   
        count = defaultdict(int)
        for _ in range(self.BOARD_SIZE):
            count[self.board[x][y]] += 1
            x += dx
            y += dy

        if datatype == "dict":
            return count
        else:
            return Markpat(count[self.last_turn], count[self.turn], count[Marubatsu.EMPTY])  
    
    def enum_markpats(self) -> set[tuple[int, int, int]]:
        """局面のマークのパターンを列挙する.
        
        Returns:
            局面のマークのパターンを要素として持つ set
            マークのパターンは、`count_marks` によって計算された返り値で
            (直前の手番のマークの数、現在の手番のマークの数、空のマスの数) を要素とする tuple
        """    

        markpats = set()
    
        # 横方向と縦方向の判定
        for i in range(self.BOARD_SIZE):
            count = self.count_marks(coord=[0, i], dx=1, dy=0, datatype="tuple")
            markpats.add(count)
            count = self.count_marks(coord=[i, 0], dx=0, dy=1, datatype="tuple")
            markpats.add(count)
        # 左上から右下方向の判定
        count = self.count_marks(coord=[0, 0], dx=1, dy=1, datatype="tuple")
        markpats.add(count)
        # 右上から左下方向の判定
        count = self.count_marks(coord=[2, 0], dx=-1, dy=1, datatype="tuple")
        markpats.add(count)

        return markpats

    def count_markpats(self) -> defaultdict[tuple[int, int, int], int]:
        """局面のマークのパターンの数を数える.
        
        Returns:
            局面のマークのパターンをキー、マークのパターンの数をキーの値として持つ defaultdict
            マークのパターンは、`count_marks` によって計算された返り値で
            (直前の手番のマークの数、現在の手番のマークの数、空のマスの数) を要素とする tuple
        """    
        
        markpats = defaultdict(int)
    
        # 横方向と縦方向の判定
        for i in range(self.BOARD_SIZE):
            count = self.count_marks(coord=[0, i], dx=1, dy=0, datatype="tuple")
            markpats[count] += 1
            count = self.count_marks(coord=[i, 0], dx=0, dy=1, datatype="tuple")
            markpats[count] += 1
        # 左上から右下方向の判定
        count = self.count_marks(coord=[0, 0], dx=1, dy=1, datatype="tuple")
        markpats[count] += 1
        # 右上から左下方向の判定
        count = self.count_marks(coord=[2, 0], dx=-1, dy=1, datatype="tuple")
        markpats[count] += 1

        return markpats   
           
class Marubatsu_GUI:
    """ 〇×ゲームの GUI.

    Attributes:
        インスタンス属性。mb 以外は play メソッドの仮引数と同じ
        mb:
            GUI を表示する Marubatsu ゲームのインスタンス
        ai (list):
            それぞれの手番を誰が担当するかを指定する list
        ai_dict (dict):
            Dropdown で選択できる AI の一覧を表す dict
        params (list):
            それぞれの AI に渡すパラメータを要素として持つ list
        size (int):
            gui が True の場合に描画するゲーム盤の画像のサイズ
    """
    
    def __init__(self, mb, ai_dict=None, size=3):
        """ GUI のウィジェットの作成などの初期設定を行う.
        
        Args:
            Marubatsu_GUI の属性と同じ
        """
        
        # ai_dict が None の場合は、空の list で置き換える
        if ai_dict is None:
            ai_dict = {}

        self.mb = mb
        self.ai_dict = ai_dict
        self.size = size

        # ai_dict が None の場合は、空の list で置き換える
        if ai_dict is None:
            self.ai_dict = {}

        # %matplotlib widget のマジックコマンドを実行する
        get_ipython().run_line_magic('matplotlib', 'widget')
        
        self.disable_shortcutkeys()
        self.create_widgets()
        self.create_event_handler()
        self.display_widgets() 
            
    @staticmethod
    def disable_shortcutkeys():
        """matplotlib のショートカットキーを禁止する"""
        
        attrs = [ "fullscreen", "home", "back", "forward", "pan", "zoom", "save", "help",
                "quit", "quit_all", "grid", "grid_minor", "yscale", "xscale", "copy"]
        for attr in attrs:
            mlp.rcParams[f"keymap.{attr}"] = []        
        
    def create_dropdown(self):
        """AI を選択する Dropdown を作成する."""
 
        # それぞれの手番の担当を表す Dropdown の項目の値を記録する list を初期化する
        select_values = []
        # 〇 と × の Dropdown を格納する list
        self.dropdown_list = []
        # ai に代入されている内容を ai_dict に追加する
        for i in range(2):
            # ラベルと項目の値を計算する
            if self.mb.ai[i] is None:
                label = "人間"
                value = "人間"
            else:
                label = self.mb.ai[i].__name__        
                value = self.mb.ai[i]
            # value を select_values に常に登録する
            select_values.append(value)
            # value が ai_values に登録済かどうかを判定する
            if value not in self.ai_dict.values():
                # 項目を登録する
                self.ai_dict[label] = value
        
            # Dropdown の description を計算する
            description = "〇" if i == 0 else "×"
            self.dropdown_list.append(
                widgets.Dropdown(
                    options=self.ai_dict,
                    description=description,
                    layout=widgets.Layout(width="100px"),
                    style={"description_width": "20px"},
                    value=select_values[i],
                )
            )      
        
    @staticmethod
    def create_button(description:str, width:int) -> widgets.Button:
        """ボタンのウィジェットを作成する.
            
        Args:        
            description:
                ボタンに表示する文字列
            width:
                ボタンの横幅
        """
        return widgets.Button(
            description=description,
            layout=widgets.Layout(width=f"{width}px"),
            style={"button_color": "lightgreen"},
        )        
        
    def create_figure(self):
        """ゲーム盤を描画する Figure を作成する."""
        self.fig, self.ax = plt.subplots(figsize=[self.size, self.size])
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False           
        
    def create_widgets(self):
        """ウィジェットを作成する."""

        # AI を選択する Dropdown を作成する
        self.create_dropdown()
        # 変更、リセット、待ったボタンを作成する
        self.change_button = self.create_button("変更", 50)
        self.reset_button = self.create_button("リセット", 80)
        self.undo_button = self.create_button("待った", 60)    
        
        # リプレイのボタンとスライダーを作成する
        self.first_button = self.create_button("<<", 50)
        self.prev_button = self.create_button("<", 50)
        self.next_button = self.create_button(">", 50)
        self.last_button = self.create_button(">>", 50)     
        self.slider = widgets.IntSlider(layout=widgets.Layout(width="200px"))
        # ゲーム盤の画像を表す figure を作成する
        self.create_figure()          
    
    def display_widgets(self):
        """ ウィジェットを配置して表示する."""

        # 〇 と × の dropdown とボタンを横に配置した HBox を作成する
        hbox1 = widgets.HBox([self.dropdown_list[0], self.dropdown_list[1], self.change_button, self.reset_button, self.undo_button])
        # リプレイ機能のボタンを横に配置した HBox を作成する
        hbox2 = widgets.HBox([self.first_button, self.prev_button, self.next_button, self.last_button, self.slider]) 
        # hbox1 と hbox2 を縦に配置した VBox を作成し、表示する
        display(widgets.VBox([hbox1, hbox2]))  
            
    @staticmethod
    def set_button_status(button, disabled:bool):
        """ ボタンのウィジェットの状態を設定する
    
        Args:
            button:
                ボタンのウィジェット
            disabled:
                False の場合は緑色で表示し、操作できるようにする
                True の場合は灰色で表示し、操作できないようにする
        """
        
        button.disabled = disabled
        button.style.button_color = "lightgray" if disabled else "lightgreen"

    def update_widgets_status(self):
        """ウィジェットの状態を更新する."""
        
        self.set_button_status(self.undo_button, self.mb.move_count < 2 or self.mb.move_count != len(self.mb.records) - 1)
        self.set_button_status(self.first_button, self.mb.move_count <= 0)
        self.set_button_status(self.prev_button, self.mb.move_count <= 0)
        self.set_button_status(self.next_button, self.mb.move_count >= len(self.mb.records) - 1)
        self.set_button_status(self.last_button, self.mb.move_count >= len(self.mb.records) - 1)    
        # value 属性よりも先に max 属性に値を代入する必要がある点に注意！
        self.slider.max = len(self.mb.records) - 1
        self.slider.value = self.mb.move_count
       
    def create_event_handler(self):
        """イベントハンドラを定義し、ウィジェットに結び付ける."""
 
        # 変更ボタンのイベントハンドラを定義する
        def on_change_button_clicked(b):
            for i in range(2):
                self.mb.ai[i] = None if self.dropdown_list[i].value == "人間" else self.dropdown_list[i].value
            self.mb.play_loop(self)

        # リセットボタンのイベントハンドラを定義する
        def on_reset_button_clicked(b=None):
            self.mb.restart()
            on_change_button_clicked(b)

        # 待ったボタンのイベントハンドラを定義する
        def on_undo_button_clicked(b=None):
            if self.mb.move_count >= 2 and self.mb.move_count == len(self.mb.records) - 1:
                self.mb.move_count -= 2
                self.mb.records = self.mb.records[0:self.mb.move_count+1]
                self.mb.change_step(self.mb.move_count)
                self.draw_board()
            
        # イベントハンドラをボタンに結びつける
        self.change_button.on_click(on_change_button_clicked)
        self.reset_button.on_click(on_reset_button_clicked)   
        self.undo_button.on_click(on_undo_button_clicked)   
        
        # step 手目の局面に移動する
        def change_step(step):
            self.mb.change_step(step)
            # 描画を更新する
            self.draw_board()        

        def on_first_button_clicked(b=None):
            change_step(0)

        def on_prev_button_clicked(b=None):
            change_step(self.mb.move_count - 1)

        def on_next_button_clicked(b=None):
            change_step(self.mb.move_count + 1)
            
        def on_last_button_clicked(b=None):
            change_step(len(self.mb.records) - 1)

        def on_slider_changed(changed):
            if self.mb.move_count != changed["new"]:
                change_step(changed["new"])
                
        self.first_button.on_click(on_first_button_clicked)
        self.prev_button.on_click(on_prev_button_clicked)
        self.next_button.on_click(on_next_button_clicked)
        self.last_button.on_click(on_last_button_clicked)
        self.slider.observe(on_slider_changed, names="value")
        
        # ゲーム盤の上でマウスを押した場合のイベントハンドラ
        def on_mouse_down(event):
            # Axes の上でマウスを押していた場合のみ処理を行う
            if event.inaxes and self.mb.status == Marubatsu.PLAYING:
                x = math.floor(event.xdata)
                y = math.floor(event.ydata)
                self.mb.move(x, y)                
                # 次の手番の処理を行うメソッドを呼び出す
                self.mb.play_loop(self)

        # ゲーム盤を選択した状態でキーを押した場合のイベントハンドラ
        def on_key_press(event):
            keymap = {
                "up": on_first_button_clicked,
                "left": on_prev_button_clicked,
                "right": on_next_button_clicked,
                "down": on_last_button_clicked,
                "0": on_undo_button_clicked,
                "enter": on_reset_button_clicked,            
            }
            if event.key in keymap:
                keymap[event.key]()
            else:
                try:
                    num = int(event.key) - 1
                    event.inaxes = True
                    event.xdata = num % 3
                    event.ydata = 2 - (num // 3)
                    on_mouse_down(event)
                except:
                    pass
                
        # fig の画像イベントハンドラを結び付ける
        self.fig.canvas.mpl_connect("button_press_event", on_mouse_down)     
        self.fig.canvas.mpl_connect("key_press_event", on_key_press)      

    @staticmethod
    def draw_mark(ax, x:int, y:int, mark:str, color:str="black"):
        """マークを描画する.
        
        (x, y) のマスに、mark で指定したマークの画像を color で指定した色で描画する
        
        Args:
            ax:
                マークを描画する Axes
            x:
                マークを描画する、ゲーム盤の x 座標
            y:
                マークを描画する、ゲーム盤の y 座標
            mark:
                描画するマーク
            color:
                描画するマークの色
        """    
        
        if mark == Marubatsu.CIRCLE:
            circle = patches.Circle([x + 0.5, y + 0.5], 0.35, ec=color, fill=False, lw=2)
            ax.add_artist(circle)
        elif mark == Marubatsu.CROSS:
            ax.plot([x + 0.15, x + 0.85], [y + 0.15, y + 0.85], c=color, lw="2")
            ax.plot([x + 0.15, x + 0.85], [y + 0.85, y + 0.15], c=color, lw="2")
    
    def draw_board(self):
        """ゲーム盤を描画する"""
        
        ax = self.ax
        ai = self.mb.ai
        
        # Axes の内容をクリアして、これまでの描画内容を削除する
        ax.clear()
        
        # y 軸を反転させる
        ax.invert_yaxis()
        
        # 枠と目盛りを表示しないようにする
        ax.axis("off")   
        
        # リプレイ中、ゲームの決着がついていた場合は背景色を変更する
        is_replay =  self.mb.move_count < len(self.mb.records) - 1 
        if self.mb.status == Marubatsu.PLAYING:
            facecolor = "lightcyan" if is_replay else "white"
        else:
            facecolor = "lightyellow"

        ax.figure.set_facecolor(facecolor)
            
        # 上部のメッセージを描画する
        # 対戦カードの文字列を計算する
        names = []
        for i in range(2):
            names.append("人間" if ai[i] is None else ai[i].__name__)
        ax.text(0, 3.5, f"{names[0]}　VS　{names[1]}", fontsize=20)   
        
        # ゲームの決着がついていない場合は、手番を表示する
        if self.mb.status == Marubatsu.PLAYING:
            text = "Turn " + self.mb.turn
        # 引き分けの場合
        elif self.mb.status == Marubatsu.DRAW:
            text = "Draw game"
        # 決着がついていれば勝者を表示する
        else:
            text = "Winner " + self.mb.status
        # リプレイ中の場合は "Replay" を表示する
        if is_replay:
            text += " Replay"
        ax.text(0, -0.2, text, fontsize=20)
        
        # ゲーム盤の枠を描画する
        for i in range(1, self.mb.BOARD_SIZE):
            ax.plot([0, self.mb.BOARD_SIZE], [i, i], c="k") # 横方向の枠線
            ax.plot([i, i], [0, self.mb.BOARD_SIZE], c="k") # 縦方向の枠線   

        # ゲーム盤のマークを描画する
        for y in range(self.mb.BOARD_SIZE):
            for x in range(self.mb.BOARD_SIZE):
                color = "red" if (x, y) == self.mb.last_move else "black"
                self.draw_mark(ax, x, y, self.mb.board[x][y], color)            

        self.update_widgets_status()   