# 3.7 ～ 3.9 の Python のバージョンでエラーが発生しないようにするためのインポート
from __future__ import annotations
from collections import defaultdict
from typing import NamedTuple
import random
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
        self.board_records = [deepcopy(self.board)]      
    
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
            if len(self.board_records) <= self.move_count:            
                self.board_records.append(deepcopy(self.board))
                self.records.append(self.last_move)
            else:
                self.board_records[self.move_count] = deepcopy(self.board)
                self.records[self.move_count] = self.last_move
                self.records = self.records[0:self.move_count + 1]
                self.board_records = self.board_records[0:self.move_count + 1]   
                            
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
       
        # ai_dict が None の場合は、空の list で置き換える
        if ai_dict is None:
            ai_dict = {}
        # params が None の場合のデフォルト値を設定する
        if params is None:
            params = [{}, {}]
    
        # seed が None でない場合は、seed を乱数の種として設定する
        if seed is not None:
            random.seed(seed)
    
        # gui が True の場合に、ゲーム盤を描画する画像を作成し、イベントハンドラに結びつける
        if gui:
            # %matplotlib widget のマジックコマンドを実行する
            get_ipython().run_line_magic('matplotlib', 'widget')
            
            # 1 行目の UI を作成する
            # それぞれの手番の担当を表す Dropdown の項目の値を記録する list を初期化する
            select_values = []
            # 〇 と × の Dropdown を格納する list
            dropdown_list = []
            # ai に代入されている内容を ai_dict に追加する
            for i in range(2):
                # ラベルと項目の値を計算する
                if ai[i] is None:
                    label = "人間"
                    value = "人間"
                else:
                    label = ai[i].__name__        
                    value = ai[i]
                # value を select_values に常に登録する
                select_values.append(value)
                # value が ai_values に登録済かどうかを判定する
                if value not in ai_dict.values():
                    # 項目を登録する
                    ai_dict[label] = value
            
                # Dropdown の description を計算する
                description = "〇" if i == 0 else "×"
                dropdown_list.append(
                    widgets.Dropdown(
                        options=ai_dict,
                        description=description,
                        layout=widgets.Layout(width="100px"),
                        style={"description_width": "20px"},
                        value=select_values[i],
                    )
                )
            
            # ボタンを作成するローカル関数を定義する 
            def create_button(description, width):
                return widgets.Button(
                    description=description,
                    layout=widgets.Layout(width=f"{width}px"),
                    style={"button_color": "lightgreen"},
                )
            
            # 変更、リセットボタンを作成する
            change_button = create_button("変更", 100)
            reset_button = create_button("リセット", 100)
                
            # 変更ボタンのイベントハンドラを定義する
            def on_change_button_clicked(b):
                for i in range(2):
                    ai[i] = None if dropdown_list[i].value == "人間" else dropdown_list[i].value
                self.play_loop(ai=ai, ax=ax, params=params, verbose=verbose, gui=gui)

            # リセットボタンのイベントハンドラを定義する
            def on_reset_button_clicked(b):
                self.restart()
                on_change_button_clicked(b)
                
            # イベントハンドラをボタンに結びつける
            change_button.on_click(on_change_button_clicked)
            reset_button.on_click(on_reset_button_clicked)        
            
            # 2 行目の UI を作成する
            # リプレイのボタンを作成する
            self.first_button = create_button("<<", 100)
            self.prev_button = create_button("<", 100)
            self.next_button = create_button(">", 100)
            self.last_button = create_button(">>", 100)
            
            def change_step(step):
                # step が負の場合は 0 に修正する
                step = max(0, min(len(self.board_records) - 1, step))
                # step 手目のゲーム盤のデータをコピーし、board に代入する
                self.board = deepcopy(self.board_records[step])
                # 手数を表す step を move_count に代入する
                self.move_count = step
                # 手番を計算する。step が偶数の場合は 〇 の 手番
                self.turn = Marubatsu.CIRCLE if step % 2 == 0 else Marubatsu.CROSS
                # status 属性を judget を使って計算する
                self.status = self.judge()
                # 直前の着手を計算する
                self.last_move = self.records[step]
                # 描画を更新する
                self.draw_board(ax, ai)
            
            def on_first_button_clicked(b):
                change_step(0)

            def on_prev_button_clicked(b):
                change_step(self.move_count - 1)

            def on_next_button_clicked(b):
                change_step(self.move_count + 1)
                
            def on_last_button_clicked(b):
                change_step(len(self.board_records) - 1)

            self.first_button.on_click(on_first_button_clicked)
            self.prev_button.on_click(on_prev_button_clicked)
            self.next_button.on_click(on_next_button_clicked)
            self.last_button.on_click(on_last_button_clicked)

            # 〇 と × の dropdown とボタンを横に配置した HBox を作成する
            hbox1 = widgets.HBox([dropdown_list[0], dropdown_list[1], change_button, reset_button])
            # リプレイ機能のボタンを横に配置した HBox を作成する
            hbox2 = widgets.HBox([self.first_button, self.prev_button, self.next_button, self.last_button]) 
            # hbox1 と hbox2 を縦に配置した VBox を作成し、表示する
            display(widgets.VBox([hbox1, hbox2]))        
    
            fig, ax = plt.subplots(figsize=[size, size])
            fig.canvas.toolbar_visible = False
            fig.canvas.header_visible = False
            fig.canvas.footer_visible = False
            fig.canvas.resizable = False          
            
            # ローカル関数としてイベントハンドラを定義する
            def on_mouse_down(event):
                # Axes の上でマウスを押していた場合のみ処理を行う
                if event.inaxes and self.status == Marubatsu.PLAYING:
                    x = math.floor(event.xdata)
                    y = math.floor(event.ydata)
                    self.move(x, y)                
                    self.draw_board(ax, ai)
                    # 次の手番の処理を行うメソッドを呼び出す
                    self.play_loop(ai=ai, ax=ax, params=params, verbose=verbose, gui=gui)
                    
            # fig の画像にマウスを押した際のイベントハンドラを結び付ける
            fig.canvas.mpl_connect("button_press_event", on_mouse_down)     
        else:
            ax = None

        self.restart()
        return self.play_loop(ai=ai, ax=ax, params=params, verbose=verbose, gui=gui)
    
    def play_loop(self, ai:list, ax, params:list[dict], verbose:bool, gui:bool) -> str | None:
        """〇×ゲームのゲーム開始後の繰り返し処理を行う.
        
        play メソッド内から呼び出して利用するので、仮引数と返り値の意味は play メソッドとほぼ同じ
        なので、下記は異なる内容のみ記述する
              
        Args:
            ax: ゲーム盤の描画を行う Axes
            
        Returns:
            決着がついた場合は勝者を表す文字列
            決着がついていない場合は None
        """
        
        # ゲームの決着がついていない間繰り返す
        while self.status == Marubatsu.PLAYING:
            # 現在の手番を表す ai のインデックスを計算する
            index = 0 if self.turn == Marubatsu.CIRCLE else 1
            # ゲーム盤の表示
            if verbose:
                if gui:
                    # AI どうしの対戦の場合は画面を描画しない
                    if ai[0] is None or ai[1] is None:
                        self.draw_board(ax, ai)
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
                self.draw_board(ax, ai)
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
    
    def draw_board(self, ax, ai):
        """ゲーム盤を描画する.
        
        Args:
            ax:
                ゲーム盤を描画する Axes
            ai:
                手番を担当する AI の関数を要素とする list
                ただし、人間が手番を担当する場合の要素は None になる    
        """    
 
        # Axes の内容をクリアして、これまでの描画内容を削除する
        ax.clear()
        
        # y 軸を反転させる
        ax.invert_yaxis()
        
        # 枠と目盛りを表示しないようにする
        ax.axis("off")   
        
        # ゲームの決着がついていた場合は背景色を
        facecolor = "white" if self.status == Marubatsu.PLAYING else "lightyellow"
        ax.figure.set_facecolor(facecolor)
            
        # 上部のメッセージを描画する
        # 対戦カードの文字列を計算する
        names = []
        for i in range(2):
            names.append("人間" if ai[i] is None else ai[i].__name__)
        ax.text(0, 3.5, f"{names[0]}　VS　{names[1]}", fontsize=20)   
        
        # ゲームの決着がついていない場合は、手番を表示する
        if self.status == Marubatsu.PLAYING:
            text = "Turn " + self.turn
        # 引き分けの場合
        elif self.status == Marubatsu.DRAW:
            text = "Draw game"
        # 決着がついていれば勝者を表示する
        else:
            text = "Winner " + self.status
        ax.text(0, -0.2, text, fontsize=20)
        
        # ゲーム盤の枠を描画する
        for i in range(1, self.BOARD_SIZE):
            ax.plot([0, self.BOARD_SIZE], [i, i], c="k") # 横方向の枠線
            ax.plot([i, i], [0, self.BOARD_SIZE], c="k") # 縦方向の枠線   

        # ゲーム盤のマークを描画する
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                color = "red" if (x, y) == self.last_move else "black"
                self.draw_mark(ax, x, y, self.board[x][y], color)            

        # ボタンのウィジェットの状態を設定する
        def set_button_status(button, disabled):
            button.disabled = disabled
            button.style.button_color = "lightgray" if disabled else "lightgreen"

        # ウィジェットの状態を更新する        
        def update_widgets_status():
            # 0 手目と最後の着手を行った局面で、特定のリプレイに関するボタンを操作できないようにする
            set_button_status(self.first_button, self.move_count <= 0)
            set_button_status(self.prev_button, self.move_count <= 0)
            set_button_status(self.next_button, self.move_count >= len(self.board_records) - 1)
            set_button_status(self.last_button, self.move_count >= len(self.board_records) - 1)

        update_widgets_status()   

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
    
    def __init__(self, mb, ai, ai_dict=None, params=None, size=3):
        """ GUI のウィジェットの作成などの初期設定を行う.
        
        Args:
            Marubatsu_GUI の属性と同じ
        """
        
        # ai_dict が None の場合は、空の list で置き換える
        if ai_dict is None:
            ai_dict = {}
        # params が None の場合のデフォルト値を設定する
        if params is None:
            params = [{}, {}]

        self.mb = mb
        self.ai = ai
        self.ai_dict = ai_dict
        self.ai_params = params
        self.size = size
        
        # ai_dict が None の場合は、空の list で置き換える
        if ai_dict is None:
            self.ai_dict = {}

        # %matplotlib widget のマジックコマンドを実行する
        get_ipython().run_line_magic('matplotlib', 'widget')
        
        self.create_widgets()
        self.display_widgets()    
        
    def create_dropdown(self):
        """AI を選択する Dropdown を作成する."""
        # それぞれの手番の担当を表す Dropdown の項目の値を記録する list を初期化する
        select_values = []
        # 〇 と × の Dropdown を格納する list
        self.dropdown_list = []
        # ai に代入されている内容を ai_dict に追加する
        for i in range(2):
            # ラベルと項目の値を計算する
            if self.ai[i] is None:
                label = "人間"
                value = "人間"
            else:
                label = self.ai[i].__name__        
                value = self.ai[i]
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
        # 変更、リセットボタンを作成する
        self.change_button = self.create_button("変更", 100)
        self.reset_button = self.create_button("リセット", 100)
        # リプレイのボタンを作成する
        self.first_button = self.create_button("<<", 100)
        self.prev_button = self.create_button("<", 100)
        self.next_button = self.create_button(">", 100)
        self.last_button = self.create_button(">>", 100)     
        # ゲーム盤の画像を表す figure を作成する
        self.create_figure()       
    
    def display_widgets(self):
        """ ウィジェットを配置して表示する."""

        # 〇 と × の dropdown とボタンを横に配置した HBox を作成する
        hbox1 = widgets.HBox([self.dropdown_list[0], self.dropdown_list[1], self.change_button, self.reset_button])
        # リプレイ機能のボタンを横に配置した HBox を作成する
        hbox2 = widgets.HBox([self.first_button, self.prev_button, self.next_button, self.last_button]) 
        # hbox1 と hbox2 を縦に配置した VBox を作成し、表示する
        display(widgets.VBox([hbox1, hbox2]))     
    