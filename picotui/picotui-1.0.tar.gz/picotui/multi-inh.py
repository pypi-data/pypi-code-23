class Base:
    pass

class Base1(Base):

    def __init__(self):
        print("Base1.i__init__")
#        super().__init__()

class Base2(Base):

    def __init__(self):
        print("Base2.i__init__")
#        super().__init__()


class Sub(Base1, Base2):

    def __init__(self):
#        super().__init__()
        Base1.__init__(self)
        Base2.__init__(self)



o = Sub()
print(isinstance(o, Base2))

print(isinstance(Base1(), Base2))
