"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

"""


class Ddict(dict):
    """
    Dict object where value by key and key by value is possible
    """
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return list(self.keys())[list(self.values()).index(item)]
