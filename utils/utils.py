def flat_map(f, li):
    """
    Maps values with function f recursively on all Iterables (except Strings)
    Flattened by using recursive Subgenerator Delegation
    """
    from collections.abc import Iterable
    for i in li:
        # str will cause a recursion depth error (Iterator of str returns Iterable str)
        if isinstance(i, Iterable) and not isinstance(i, str):
            yield from flat_map(f, i)
        else:
            yield f(i)


class AmbiguousStringReplacement(Exception):
    def __init__(self, text, old):
        self.text = text
        self.old = old
        self.message = f'Ambiguous String Replacement: Found {text.count(old)} occurrences of "{old}" in "{text}"'
        super().__init__(self.message)


def safe_replace(text, old, new):
    if text.count(old) != 1:
        raise AmbiguousStringReplacement(text, old)
    return text.replace(old, new)
