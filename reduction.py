# -*- coding:utf-8 -*-


class UCW(object):
    def __init__(self):
        self.Sigma_I = {'r', '!r'}
        self.Sigma_O = {'g', '!g'}
        self.Q_I = {'q2', 'q4'}
        self.Q_O = {'q1', 'q3'}
        self.Q_ini = {'q1'}
        self.alpha = {'q4'}
        self.delta_I = {('q2', 'r', 'q1'),
                        ('q2', 'r', 'q3'),
                        ('q2', '!r', 'q1'),
                        ('q4', 'r', 'q3'),
                        ('q4', '!r', 'q3'),
                        }
        self.delta_O = {('q1', 'g', 'q2'),
                        ('q1', '!g', 'q2'),
                        ('q3', '!g', 'q4'),
                        }



def all_patterns(states, K, pattern=None):
    from copy import copy
    
    if pattern is None:
        pattern = dict()
    if len(states) == 0:
        return [pattern]

    ret = []
    head = states.pop()
    tail = states
    for n in range(-1, K+2):
        cp = copy(pattern)
        cptail = copy(tail)
        cp[head] = n
        ret += all_patterns(cptail, K, cp)
    return ret


def succ(F, sigma, delta, alpha, Q, K):
    def _in_(q, alpha):
        if q in alpha:
            return 1
        else:
            return 0
    map = {}
    for q in Q:
        map[q] = -1
    
    for p, s, q in [(p, s, q) for (p, s, q) in delta
                         if s == sigma and F[p] != -1]:
        m = min(K + 1, F[p] + _in_(q, alpha))
        if q in map:
            map[q] = max(map[q], m)
        else:
            map[q] = m

    return map


def succ_1to2(F, sigma, A, K):
    return succ(F, sigma, A.delta_O, A.alpha, A.Q_I, K)


def succ_2to1(F, sigma, A, K):
    return succ(F, sigma, A.delta_I, A.alpha, A.Q_O, K)


def _calc_gamma(delta, F, A, succ, K):
    ret = set()
    for (p, s, q) in delta:
        if F[p] <= K and succ(F, s, A, K)[q] <= K:
            ret.add(s)
    return ret


def calc_gamma(A, K):
    return lambda F: _calc_gamma(A.delta_O, F, A, succ_1to2, K)


class Game(object):
    def __init__(self):
        self.Moves_1 = set()
        self.Moves_2 = set()
        self.S_1 = []
        self.S_2 = []
        self.Gamma_1 = set()
        self.Delta_1 = set()
        self.Delta_2 = set()


def G(A, K):
    g = Game()
    g.S_1 = all_patterns(A.Q_O, K)
    g.S_2 = all_patterns(A.Q_I, K)
    g.Moves_1 = A.Sigma_O
    g.Moves_2 = A.Sigma_I
    g.Gamma_1 = calc_gamma(A, K)
    g.Delta_1 = lambda F, sigma: succ_1to2(F, sigma, A, K)
    g.Delta_2 = lambda F, sigma: succ_2to1(F, sigma, A, K)
    return g
