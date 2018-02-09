#!/bin/python
#coding:utf-8
import roomai.common


class FiveCardStudAction(roomai.common.AbstractAction):
    '''
    The FiveCardStudAction. The action consists of two parts, namely option and price.\n
    The option is ["Fold","Check","Call","Raise","Bet", "Showhand"], and the price is the chips used by this action.\n
    The FiveCardStudAction has a key "%s_%d"%(option, price) as its identification. Examples of usages:\n
    >> import roomai.fivecardstud\n
    >> a = roomai.fivecardstud.FiveCardStudAction.lookup("Fold_0") \n
    >> # We strongly recommend you to get a FiveCardStudAction using the lookup function\n
    >> a.option \n
    Fold\n
    >> a.price\n
    0\n
    '''

    # 弃牌
    Fold        = "Fold"
    # 过牌
    Check       = "Check"
    # 更注
    Call        = "Call"
    # 加注
    Raise       = "Raise"
    # 下注
    Bet         = "Bet"
    # all in
    Showhand    = "Showhand"

    def __init__(self,key):
            super(FiveCardStudAction,self).__init__(key)
            opt_price = key.strip().split("_")
            if  opt_price[0] != self.Fold    and opt_price[0] != self.Call  and \
                opt_price[0] != self.Check   and opt_price[0] != self.Raise and \
                opt_price[0] != self.Bet     and opt_price[0] != self.Showhand:
                raise  ValueError("%s is an invalid key. The Option must be in [Fold,Check,Call,Raise,Bet,Showhand]"%key)

            if opt_price[0] not in  [self.Fold,self.Check, self.Call] and int(opt_price[1]) <= 0:
                raise  ValueError("%s is an invalid key.]"%key)

            if opt_price[0] == self.Fold and int(opt_price[1]) > 0:
                raise  ValueError("%s is an invalid key"%(key))

            if int(opt_price[1]) < 0:
                raise  ValueError("%s is an invalid key.]"%key)

            self.__option__ = opt_price[0]
            self.__price__  = int(opt_price[1])



    def __get_option__(self): return self.__option__
    option = property(__get_option__, doc = "The option of the action. The option must be one of \"Fold\",\"Check\",\"Call\",\"Raise\",\"Bet\",\"Showhand\".")

    def __get_price__(self): return self.__price__
    price = property(__get_price__)
    '''
    The price of the action (chips used by this action). If the action's option is \"Fold\", the price should be 0. Example of usage,\n
    >>action = roomai.fivecardstud.FiveCardStudAction.lookup(\"Bet_200\")\n
    >>acton.price\n
    200\n
    '''

    @classmethod
    def lookup(cls,key):
        return AllFiveCardStudActions[key]

    def __deepcopy__(self, memodict={}, newinstance = None):
        return self.lookup(self.key)

AllFiveCardStudActions = dict()
options = ["Fold", "Check","Call","Raise","Bet","Showhand"]
for option in options:
    if option in ["Check","Call"]:
        for p in range(100000):
            AllFiveCardStudActions["%s_%d"%(option,p)] = FiveCardStudAction("%s_%d"%(option,p))
    elif option in ["Raise","Bet","Showhand"]:
        for p in range(1,100000):
            AllFiveCardStudActions["%s_%d"%(option,p)] = FiveCardStudAction("%s_%d"%(option,p))
    else:
        AllFiveCardStudActions["Fold_0"] = FiveCardStudAction("Fold_0")
is_init_action = False
