import re


def get_words(s: str):
    s = remove_special_chars(s)
    s = remove_incomplete_chars(s)
    s = s.lower()
    return s.split()


def remove_special_chars(s: str):
    pattern = r'[^\w\s]'
    replace = ''
    return re.sub(pattern=pattern, repl=replace, string=s)


def remove_incomplete_chars(s: str):
    pattern = r'[ㄱ-ㅎㅏ-ㅣ]'
    replace = ''
    return re.sub(pattern=pattern, repl=replace, string=s)


class TqdmDummy:
    def update(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
