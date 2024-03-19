"""
Score計算用のキャッシュファイルを扱うクラス．

"""

import os
import pickle
import shutil
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
        self.__loaded_filename = None  # 現在読み込んでいるキャッシュのファイル名
        self.__values = None  # 現在持っているキャッシュの値

        # キャッシュ保管用のディレクトリを作っておく
        temp_dir = tempfile.gettempdir()
        self.__cache_dir_path = os.path.join(temp_dir, "cache")
        if os.path.exists(self.__cache_dir_path):
            shutil.rmtree(self.__cache_dir_path)
        os.mkdir(self.__cache_dir_path)

    def append(self, value):
        """
        self.__valuesにvalueを追加する関数．

        Parameters
        ----------
        value : Any
            追加するデータの値．

        """
        if self.__values is None:
            raise ValueError("No file loaded.")

        self.__values.append(value)

    def get_values(self):
        """
        self.__valuesを取ってくる．read only．

        Return
        ------
        values : list
            self.__values．

        """
        if self.__values is None:
            return None

        return self.__values

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
            with open(os.path.join(self.__cache_dir_path, self.__loaded_filename + ".pkl"), "wb") as file:
                pickle.dump(self.__values, file)

        self.__loaded_filename = filename
        self.__values = []
        if os.path.exists(os.path.join(self.__cache_dir_path, self.__loaded_filename + ".pkl")):
            with open(os.path.join(self.__cache_dir_path, self.__loaded_filename + ".pkl"), "rb") as file:
                self.__values = pickle.load(file)

    def clear(self):
        """
        このキャッシュのデータを削除する．

        """
        if self.__loaded_filename is not None and not os.path.exists(
            os.path.join(self.__cache_dir_path, self.__loaded_filename + ".pkl")
        ):
            os.remove(os.path.join(self.__cache_dir_path, self.__loaded_filename + ".pkl"))
        self.__loaded_filename = None
        self.__values = None


def main():
    from traceback import format_exc

    cache = Cache()
    try:
        cache.append({"TrialNo": "1", "Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": True})
    except Exception:
        print(format_exc())
    cache.load("Match#1#Team#1")
    cache.append({"TrialNo": "1", "Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": True})
    cache.load("Match#1#Team#1")
    cache.append({"TrialNo": "2", "Objective": 0.2, "Constraint": None, "Info": {}, "Score": 0.2, "Feasible": False})
    cache.load("Match#1#Team#1")
    cache.append({"TrialNo": "3", "Objective": 0.01, "Constraint": None, "Info": {}, "Score": 0.01, "Feasible": None})
    cache.load("Match#1#Team#2")
    cache.append({"TrialNo": "1", "Objective": 0.3, "Constraint": None, "Info": {}, "Score": 0.3, "Feasible": None})
    cache.load("Match#1#Team#1")
    print(cache.get_values())
    cache.load("Match#1#Team#2")
    print(cache.get_values())
    cache.clear()
    print(cache.get_values())
    cache.load("Match#1#Team#1")
    print(cache.get_values())
    cache.load("Match#1#Team#2")
    cache.clear()
    try:
        cache.append({"TrialNo": "1", "Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": None})
    except Exception:
        print(format_exc())


if __name__ == "__main__":
    main()
