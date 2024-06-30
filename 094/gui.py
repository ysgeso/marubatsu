from abc import ABCMeta, abstractmethod
import matplotlib as mlp
import ipywidgets as widgets

class GUI(metaclass=ABCMeta):
    """GUI の処理を行うクラスの基底クラス."""

    def __init__(self):
        # %matplotlib widget のマジックコマンドを実行する
        get_ipython().run_line_magic('matplotlib', 'widget')
        
        self.disable_shortcutkeys()
        self.create_widgets()
        self.create_event_handler()
        self.display_widgets() 
   
    @abstractmethod
    def create_widgets(self):
        """ウィジェットを作成する."""        
        pass
    
    @abstractmethod
    def create_event_handler(self):
        """イベントハンドラを定義する."""        
        pass
    
    @abstractmethod
    def display_widgets(self):
        """ウィジェットを配置して表示する."""
        pass

    @abstractmethod
    def update_gui(self):
        """GUI の表示を更新する."""
        pass

    @abstractmethod
    def update_widgets_status(self):
        """ウィジェットの状態を更新する."""
        pass

    @staticmethod
    def disable_shortcutkeys():
        """matplotlib の Figure のデフォルトのショートカットキー操作を禁止する."""
        
        attrs = [ "fullscreen", "home", "back", "forward", "pan", "zoom", "save", "help",
                "quit", "quit_all", "grid", "grid_minor", "yscale", "xscale", "copy"]
        for attr in attrs:
            mlp.rcParams[f"keymap.{attr}"] = []     
            
    @staticmethod
    def create_button(description:str, width:float):   
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