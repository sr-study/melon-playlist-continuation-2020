import re


def get_words(s: str):
    s = remove_special_chars(s)
    s = remove_incomplete_chars(s)
    s = s.lower()
    return s.split()


def remove_special_chars(s: str):
    pattern = '[^\w\s]'
    replace = ''
    return re.sub(pattern=pattern, repl=replace, string=s)


def remove_incomplete_chars(s: str):
    pattern = '[ㄱ-ㅎㅏ-ㅣ]'
    replace = ''
    return re.sub(pattern=pattern, repl=replace, string=s)
