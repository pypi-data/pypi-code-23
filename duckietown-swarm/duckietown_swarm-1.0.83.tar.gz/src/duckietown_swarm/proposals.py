from duckietown_swarm.intervals_utils import interval_friendly
import time
from contracts import contract

ANONYMOUS = 'anonymous'


class Proposal(object):

    @contract(validity='seq[2](int|None)', who='str')
    def __init__(self, validity, who):
        self.validity = tuple(validity)
        self.who = who

    def __eq__(self, b):
        return (self.validity == b.validity) and (self.who == b.who)

    def __hash__(self):
        return hash((self.validity, self.who))

    def __repr__(self):
        s = interval_friendly(self.validity)
        s += ' proposed by %r' % self.who
        return s

    @staticmethod
    def strictly_dominates(a, b, t=None):
        if t is None: t = time.time()
        ok1 = interval_strictly_dominates(a.validity, b.validity, t) and \
              who_dominates(a.who, b.who)
        ok2 = interval_dominates(a.validity, b.validity, t) and \
              who_strictly_dominates(a.who, b.who)
        return ok1 or ok2

    @staticmethod
    def dominates(a, b, t=None):
        if t is None: t = time.time()
        return interval_dominates(a.validity, b.validity, t) and \
              who_dominates(a.who, b.who)


def who_strictly_dominates(who1, who2):
    return who2 == ANONYMOUS and who1 != ANONYMOUS


def who_dominates(who1, who2):
    return (who1 == who2) or who_strictly_dominates(who1, who2)

#def signatures_dominate(s1, s2):
#    return s1.issuperset(s2)
#
#
#def signatures_strictly_dominate(s1, s2):
#    return s1.issuperset(s2) and (s1 != s2)


def interval_dominates(v1, v2, t=None):
    if t is None: t = time.time()
    return interval_strictly_dominates(v1, v2, t) or (v1 == v2)


def interval_strictly_dominates(v1, v2, t=None):
    if t is None: t = time.time()
    v1 = interval_cut(v1, t)
    v2 = interval_cut(v2, t)

    start_1, end_1 = v1
    start_2, end_2 = v2

    if end_1 is None: end_1 = float('inf')
    if end_2 is None: end_2 = float('inf')

    ok1 = (start_1 <= start_2) and (end_1 > end_2)
    ok2 = (start_1 < start_2) and (end_1 >= end_2)
    return ok1 or ok2


#    @contract(returns=Proposal)
def interval_cut(validity, t):
    ''' Returns a new interval cut
        at time t -- "let's forget about the past" '''
    t0, t1 = validity
    if t0 is None:
        t0_ = t
    else:
        t0_ = max(t0, t)
    return (t0_, t1)


@contract(proposal=Proposal, proposals='set($Proposal)', returns='set($Proposal)')
def strictly_dominated_by_set(proposal, proposals):
    ''' Retuns a set of proposals that dominate this one. '''
    doms = set()
    for p in proposals:
        if Proposal.strictly_dominates(p, proposal):
            doms.add(p)
    return doms
#
#    if proposal.signatures:
#        doms = set()
#        # all signatures must be dominated
#        for s in proposal.signatures:
#            p2 = Proposal(proposal.validity, [s])
#            doms_s = set()
#            for existing in proposals:
#                if Proposal.strictly_dominates(existing, p2):
#                    doms_s.add(existing)
#            if not doms_s:
#                # p2 was not dominated
#                return set()
#            doms.update(doms_s)
#        return doms
#    else:
#        doms = set()
#        for existing in proposals:
#            if Proposal.strictly_dominates(existing, proposal):
#                doms.add(existing)
#        return doms

#
#
#def strictly_dominates(validity1, validity2, t):
#    start_1, end_1 = validity1
#    start_2, end_2 = validity2
#
#    if start_1 is None:
#        start_1 = 0
#    if start_2 is None:
#        start_2 = 0
#    if end_1 is None:
#        end_1 = t * 2
#    if end_2 is None:
#        end_2 = t * 2
#    start_1 = max(t, start_1)
#    start_2 = max(t, start_2)
#    ok1 = (start_1 <= start_2) and (end_1 > end_2)
#    ok2 = (start_1 < start_2) and (end_1 >= end_2)
#
#    return ok1 or ok2
