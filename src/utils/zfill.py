def zfill(number, digit):
    """
    numberをdigit桁でゼロ埋めする関数．
    ゼロ埋めしたnumberの桁数がdigitを超える場合はエラーとなる．
    
    Parameters
    ----------
    number : int
        ゼロ埋めする数字．
    digit : int
        ゼロ埋めする桁数．

    Return
    ------
    number ; str
        ゼロ埋めした数字．

    """
    number = str(number).zfill(digit)
    
    if len(number) != digit:
        raise ValueError("length of number != digit.")
    
    return number
