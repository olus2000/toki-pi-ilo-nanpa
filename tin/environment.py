class Environment:

    def __init__(self, parent=None):
        self.parent = parent
        if parent is None:
            self.grandparent = self
        else:
            self.grandparent = parent.grandparent
        self.data = {}

    def get_local(self, k):
        if k in self.data:
            return self.data[k]
        else:
            return None

    def set_local(self, k, v):
        self.data[k] = v

    def get_first(self, k):
        while k not in self.data and self.parent is not None:
            self = self.parent
        if k in self.data:
            return self.data[k]
        else:
            return None

    def set_first(self, k, v):
        while k not in self.data and self.parent is not None:
            self = self.parent
        self.data[k] = v

    def get_global(self, k):
        if k in self.grandparent:
            return self.grandparent.data[k]
        else:
            return None

    def set_global(self, k, v):
        self.grandparent.data[k] = v
