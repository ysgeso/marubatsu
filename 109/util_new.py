from marubatsu import Marubatsu
import ai as ai_module
import pickle
import gzip
from tqdm import tqdm

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
    
def load_bestmoves(fname:str="../data/bestmoves.dat"):
    """各局面の最善手の一覧を表すデータをファイルから読み込む

    Args:
        fname:
            データファイルのパス

    Returns:
        読み込んだデータ
    """

    with gzip.open(fname, "rb") as f:
        return pickle.load(f)
    
def load_mblist(fname:str="../data/mblist.dat"):
    """決着がついていない局面を表すデータをファイルから読み込む

    Args:
        fname:
            データファイルのパス

    Returns:
        読み込んだデータ
    """

    with gzip.open(fname, "rb") as f:
        return pickle.load(f)    
    
class Check_solved:
    """AI が解決されているかどうかを判定するクラス

    Attributes:
        クラス属性
        bestmoves(dict[tuple]):
            各局面の最善手の一覧を表すデータ
        mblist(list[Marubatsu]):
            決着がついていない局面を表す list
    """

    bestmoves = load_bestmoves()
    mblist = load_mblist()
    
    @staticmethod
    def is_strongly_solved(ai):
        """強解決の AI であるかどうかを判定する.
        
        判定の処理の際に、最善手のみを選択する局面の数を表示する.
        
        Args:
            ai:
                判定する AI
        
        Returns:
            強解決の AI の場合は True、そうでない場合は False を返す
        """
        count = 0
        for mb in tqdm(Check_solved.mblist):
            if set(ai(mb, candidate=True)) <= set(Check_solved.bestmoves[tuple(mb.records)]):
                count += 1
        nodenum = len(Check_solved.mblist)
        print(f"{count}/{nodenum} {count/nodenum*100:.2f}%")
        return count == nodenum
