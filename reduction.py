# -*- coding:utf-8 -*-

import pygraphviz as pgv


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



def dict2func(dic):
    return lambda k: dic[k]
        

def create_S(states, K, pattern=None):
    from copy import copy
    
    if pattern is None:
        pattern = dict()
    if len(states) == 0:
        return {dict2func(pattern)}

    ret = set()
    head = states.pop()
    tail = states
    for n in range(-1, K+2):
        cp = copy(pattern)
        cptail = copy(tail)
        cp[head] = n
        ret.update(create_S(cptail, K, cp))
    return ret


def succ(F, sigma, delta, alpha, Q, K):
    def _in_(q, alpha):
        if q in alpha:
            return 1
        else:
            return 0
    map = {q: -1 for q in Q}
    
    for p, s, q in [(p, s, q) for (p, s, q) in delta
                         if s == sigma and F(p) != -1]:
        m = min(K + 1, F(p) + _in_(q, alpha))
        map[q] = max(map[q], m)

    return dict2func(map)


def succ_1to2(F, sigma, A, K):
    return succ(F, sigma, A.delta_O, A.alpha, A.Q_I, K)


def succ_2to1(F, sigma, A, K):
    return succ(F, sigma, A.delta_I, A.alpha, A.Q_O, K)


def calc_gamma(A, K):
    def inner(F):
        ret = set()
        for (p, s, q) in A.delta_O:
            if F(p) <= K and succ_1to2(F, s, A, K)(q) <= K:
                ret.add(s)
        return ret
    return lambda F: inner(F)


def calc_F_0(S_1, Q_O, Q_ini, alpha):
    F_0 = set()
    for F in S_1:
        for q in Q_O:
            if not ((q not in Q_ini and F(q) == -1) or
                    (q in Q_ini and q not in alpha and F(q) == 0) or
                    (q in Q_ini and q in alpha and F(q) == 1)):
                break
        else:
            F_0.add(F)
    return F_0


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
    from copy import copy
    g = Game()
    g.S_1 = create_S(copy(A.Q_O), K)
    g.S_2 = create_S(copy(A.Q_I), K)
    g.Moves_1 = A.Sigma_O
    g.Moves_2 = A.Sigma_I
    g.Gamma_1 = calc_gamma(A, K)
    g.Delta_1 = lambda F, sigma: succ_1to2(F, sigma, A, K)
    g.Delta_2 = lambda F, sigma: succ_2to1(F, sigma, A, K)
    return g


def tostring_F(F, Q):
    return ', '.join(['({0}, {1})'.format(q, F(q)) for q in Q if F(q) != -1])

    
def convert_iter(G, F, Q_I, Q_O, turn, visited, graph):
    if turn == 1:
        Q = Q_O
        Q_next = Q_I
        next_turn = 2
        sigmas = G.Gamma_1(F)
        Delta = G.Delta_1
        node_shape = 'ellipse'
        node_shape_next = 'box'
    else:
        Q = Q_I
        Q_next = Q_O
        next_turn = 1
        sigmas = G.Moves_2
        Delta = G.Delta_2
        node_shape = 'box'
        node_shape_next = 'ellipse'

    string_F = tostring_F(F, Q)
    if string_F in visited:
        return
    visited.add(string_F)
    graph.add_node(string_F, shape=node_shape)
    for s in sigmas:
        F_next = Delta(F, s)
        string_F_next = tostring_F(F_next, Q_next)
        graph.add_node(string_F_next, shape=node_shape_next)
        edge = find_edge(graph, string_F, string_F_next)
        if edge is not None:
            label = edge.attr['label']
            s = ', '.join([s, label])
        graph.add_edge(string_F, string_F_next, label=s, dir='forward')
        convert_iter(G, F_next, Q_I, Q_O, next_turn, visited, graph)

def find_edge(graph, start, end):
    if graph.has_edge(start, end):
        for edge in graph.edges_iter(start):
            if edge[1] == end:
                return edge
    return None    

def convert(A, K):
    graph = pgv.AGraph(directed=True)
    g = G(A, K)
    F_0 = calc_F_0(g.S_1, A.Q_O, A.Q_ini, A.alpha)
    for f_0 in F_0:
        visited = set()
        convert_iter(g, f_0, A.Q_I, A.Q_O, 1, visited, graph)
    graph.layout(prog='dot')
    graph.draw('ret.png')
    return graph
