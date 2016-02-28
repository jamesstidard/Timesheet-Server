"""
Created on 27 Oct 2015

@author: peterb
"""


class DotDict(dict):
    """
        A dict that allows for object-like property access syntax.
    """

    def __getattr__(self, name):
        if name[0] == '_':
            return dict.__getattr__(self.name)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
