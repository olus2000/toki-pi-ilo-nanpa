class Environment:

    def __init__(self, parent=None):
        self.parent = parent
        self.data = {}

    def get_local(self, k):
        if k in self.data:
            return self.data[k]
        else:
            return None

    def set_local(self, k, v):
        self.data[k] = v

    def get_first(self, k):
        if k in self.data:
            return self.data[k]
        elif self.parent is None:
            return None
        else:
            return self.parent.get_first(k)

    def set_first(self, k, v):
        if k in self.data or self.parent is None:
            self.data[k] = v
        else:
            self.parent.set_first(k, v)

    def get_global(self, k):
        if self.parent is not None:
            return self.parent.get_global(k)
        elif k in self.data:
            return self.data[k]
        else:
            return None

    def set_global(self, k, v):
        if self.parent is not None:
            self.parent.set_global(k, v)
        else:
            self.data[k] = v
