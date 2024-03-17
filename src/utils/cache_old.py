"""
Score計算用のキャッシュファイルを扱うクラス．

"""
import os
import shutil
import shelve
import tempfile

"""
評価に使うHistoryを作成する．
CacheとDynamo DBがあればできる


"""

class Cache:
    """
    Score計算用のキャッシュファイルを扱うクラス．

    """

    def __init__(self):
        """
        キャッシュの初期化．

        """
        self.__loaded_filename = None # 現在読み込んでいるキャッシュのファイル名
        self.__values = None # 現在持っているキャッシュの値

        # キャッシュ保管用のディレクトリを作っておく
        temp_dir = tempfile.gettempdir()
        self.__cache_dir_path = os.path.join(temp_dir, "cache")
        if os.path.exists(self.__cache_dir_path):
            shutil.rmtree(self.__cache_dir_path)
        os.mkdir(self.__cache_dir_path)
        

    def append(self, key, value):
        """
        self.__valuesにkey:valueを追加する関数．

        Parameters
        ----------
        key : str
            追加するデータのキー．
        value : Any
            追加するデータの値．

        """
        if self.__values is None:
            raise ValueError("No file loaded.")
        
        self.__values[key] = value


    def get_values(self):
        """
        self.__valuesを取ってくる．read only．
        
        Return
        ------
        values : dict
            self.__values．

        """
        if self.__values is None:
            return None
        
        return self.__values
    

    def get_length_of_values(self):
        """
        self.__valuesの長さ(すなわち，キャッシュに入っているデータの数)を取ってくる．
        
        Return
        ------
        length : int
            self.__valuesの長さ．

        """
        if self.__values is None:
            return None
        
        return len(self.__values)
    
    
    def load(self, filename):
        """
        filenameのキャッシュからデータを取ってくる．

        Parameter
        ---------
        filename : str
            キャッシュファイル名．
        
        """
        if self.__loaded_filename is not None and filename == self.__loaded_filename:
            return
        
        if self.__loaded_filename is not None:
            with shelve.open(os.path.join(self.__cache_dir_path, self.__loaded_filename)) as cache:
                for key in self.__values:
                    cache[key] = self.__values[key]

        self.__values = {}    
        self.__loaded_filename = filename
        with shelve.open(os.path.join(self.__cache_dir_path, self.__loaded_filename)) as cache:
                for key in cache:
                    self.__values[key] = cache[key]


    def clear(self):
        """
        このキャッシュのデータを削除する．

        """
        if self.__loaded_filename is not None:
            os.remove(os.path.join(self.__cache_dir_path, self.__loaded_filename + ".db"))
            self.__loaded_filename = None
            self.__values = None
    

def main():
    from traceback import format_exc
    cache = Cache()
    try:
        cache.append("1", {"Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": True})
    except Exception:
        print(format_exc())
    cache.load("Match#1#Team#1")
    cache.append("1", {"Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": True})
    cache.load("Match#1#Team#1")
    cache.append("2", {"Objective": 0.2, "Constraint": None, "Info": {}, "Score": 0.2, "Feasible": False})
    cache.load("Match#1#Team#1")
    cache.append("3", {"Objective": 0.01, "Constraint": None, "Info": {}, "Score": 0.01, "Feasible": None})
    cache.load("Match#1#Team#2")
    cache.append("1", {"Objective": 0.3, "Constraint": None, "Info": {}, "Score": 0.3, "Feasible": None})
    cache.load("Match#1#Team#1")
    values = cache.get_values()
    print(cache.get_length_of_values(), cache.get_values())
    values["1"]["Objective"] = 1.0
    print(cache.get_length_of_values(), cache.get_values())
    cache.load("Match#1#Team#2")
    print(cache.get_length_of_values(), cache.get_values())
    cache.clear()
    print(cache.get_length_of_values(), cache.get_values())
    try:
        cache.append("1", {"Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": None})
    except Exception:
        print(format_exc())
    


if __name__ == "__main__":
    main()
        
