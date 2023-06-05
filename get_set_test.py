class GetSetTest():
    def __init__(self, value):
        self.attrval = None
        self.var = value

    @property
    def var(self):
        print('getting the "var" attribute')
        return self.attrval

    @var.setter
    def var(self, value):
        print('setting the "var" attribute')
        self.attrval = value

    @var.deleter
    def var(self):
        print('deleting the "var" attribute')
        self.attrval = None


if __name__ == '__main__':
    g = GetSetTest(10)
    print(g.var)
    print(g.attrval)
    g.var = 20
    print(g.var)
    print(g.attrval)
    del g.var
    print(g.var)
    print(g.attrval)
