"""
Score計算用のキャッシュファイルを扱うクラス．

"""
import os
import shelve
import tempfile
from copy import deepcopy



class Cache:
    """
    Score計算用のキャッシュファイルを扱うクラス．

    """

    def __init__(self, loaded_cachename):
        """
        キャッシュの初期化．

        Parameter
        ---------
        loaded_filename : str
            現在読み込んでいるキャッシュ名．

        """
        self.__loaded_cachename = loaded_cachename # 現在読み込んでいるキャッシュのファイル名
        self.__values = {} # 現在持っているキャッシュの値

        # キャッシュ保管用のディレクトリを作っておく
        temp_dir = tempfile.gettempdir()
        self.__cache_dir_path = os.path.join(temp_dir, "cache")
        if not os.path.exists(self.__cache_dir_path):
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
        self.__values[key] = value


    def get_values(self):
        """
        self.__valuesを取ってくる．
        
        Return
        ------
        values : dict
            self.__values．

        """
        return deepcopy(self.__values)
    

    def get_length_of_values(self):
        """
        self.__valuesの長さ(すなわち，キャッシュに入っているデータの数)を取ってくる．
        
        Return
        ------
        length : int
            self.__valuesの長さ．

        """
        return len(self.__values)
    
    
    def load(self, cachename):
        """
        cachenameのキャッシュからデータを取ってくる．

        Parameter
        ---------
        cachename : str
            キャッシュファイル名．
        
        """
        if cachename == self.__loaded_cachename:
            return
        

        with shelve.open(os.path.join(self.__cache_dir_path, self.__loaded_cachename)) as cache:
            for key in self.__values:
                cache[key] = self.__values[key]

        self.__values = {}    
        self.__loaded_cachename = cachename
        with shelve.open(os.path.join(self.__cache_dir_path, self.__loaded_cachename)) as cache:
                for key in cache:
                    self.__values[key] = cache[key]  


    def clear(self):
        """
        このキャッシュのデータを削除する．

        """
        os.remove(os.path.join(self.__cache_dir_path, self.__loaded_cachename + ".db"))
        self.__values = {}
    

def main():
    cache = Cache("Match#1#Team#1")
    cache.append("1", {"Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8})
    cache.load("Match#1#Team#1")
    cache.append("2", {"Objective": 0.2, "Constraint": None, "Info": {}, "Score": 0.2})
    cache.load("Match#1#Team#1")
    cache.append("3", {"Objective": 0.01, "Constraint": None, "Info": {}, "Score": 0.01})
    cache.load("Match#1#Team#2")
    cache.append("1", {"Objective": 0.3, "Constraint": None, "Info": {}, "Score": 0.3})
    cache.load("Match#1#Team#1")
    values = cache.get_values()
    print(cache.get_values())
    values["1"]["Objective"] = 1.0
    print(cache.get_values())
    cache.clear()
    cache.load("Match#1#Team#2")
    print(cache.get_values())
    cache.clear()


if __name__ == "__main__":
    main()
        
