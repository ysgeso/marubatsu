from marubatsu import Marubatsu
import ai as ai_module

def gui_play(ai=None, ai_dict=None, seed:int|None=None):
    """GUI で 〇×ゲームを遊ぶ
    
        Marubatsu クラスのインスタンスを作成し、play メソッドを呼び出す処理を行う
        そのため、仮引数 ai と ai_dict は play メソッドと同じ意味を持つ
              
        Args:
            ai: それぞれの手番を担当する AI の関数を要素として持つ list
                実引数を省略した場合は、人間どうしの対戦を行う
            ai_list:
                Dropdown で選択できる AI の項目を表す dict
                実引数を省略した場合は、ai1s ～ ai14s の項目を表す dict を作成する
            seed:
                最初のゲーム利用する乱数の種
    """

    # ai が None の場合は、人間どうしの対戦を行う
    if ai is None:
        ai = [None, None]
    # ai_dict が None の場合は、ai1s ~ ai14s の Dropdown を作成するためのデータを計算する
    if ai_dict is None:
        ai_dict = { "人間": "人間"}
        for i in range(1, 15):
            ai_name = f"ai{i}s"  
            ai_dict[ai_name] = getattr(ai_module, ai_name)
    
    mb = Marubatsu()
    mb.play(ai=ai, ai_dict=ai_dict, seed=seed, gui=True)