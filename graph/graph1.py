from numpy import array, linalg
from collections import defaultdict
import time
# from functools import wraps

PROF_DATA = {}

def profile(fn):
#     @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()
        ret = fn(*args, **kwargs)
        elapsed_time = time.time() - start_time
        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)
        return ret
    return with_profiling

def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print("Function %s called %d times." % (fname, data[0]))
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))
        #print('Time series', data[1])

def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}

M = array([[1, 0, 0, 1], [0, 0, 1, 1], [1, 1, 0, 0], [0, 1, 0, 0]])
V1 = array([0, 0, 0, 0])
V2 = array([1, 0, 0, 0])
V3 = array([0, 0, 0, 1])
LAMB_Q = linalg.eig(M)
Q_1 = linalg.inv(LAMB_Q[1])
L = LAMB_Q[0]
lam_2 = L[2]
TAU3 = Q_1[2]

GRAPH = [(0, 0, V1), (0, 1, V2), 
         (1, 2, V1), 
         (2, 1, V3), (2, 3, V1),
         (3, 2, V2), (3, 0, V1)]


def create_graph(connections):
    graph = defaultdict(set)
    vectors = {}
    for node1, node2, vector in connections:
        graph[node1].add(node2)
        vectors[10 * node1 + node2] = vector
    return graph, vectors

# def is_connected(graph, node1, node2):
#     return node1 in graph and node2 in graph[node1]

def get_vector(graph, node1, node2):
    return vectors[10 * node1 + node2]

# neni optimalni pro velke delky
def find_paths(graph, start, length):
    if length == 0:
        return [[start]]
    paths = [[start] + path for _next in graph[start] for path in find_paths(graph, _next, length - 1)]
    return paths

@profile
def find_all_paths(graph, length):
    paths = []
    for node in graph.keys():
        paths.extend(find_paths(graph, node, length))
    return paths

# def find_vectors(graph, vectors, start, length):
#     if length == 0:
#         return []
#     paths = [get_vector(start, _next) + path for _next in graph[start] for path in find_paths(graph, _next, length - 1)]
#     return paths

def path_value(vectors, path):
    if not path or len(path) == 1:
        return None
    start = path[0]
    value = None
    for node in path[1:]:
        vector = vectors[10 * start + node]
        if value is None:
            value = vector
        else:
            value = M @ value + vector
        start = node
#     print('p-v', path, value)
    return value

# def node_values(graph, vectors, start, length):
#     values = []
#     paths = find_paths(graph, start, length)
#     for path in paths:
#         values.append(path_value(vectors, path))
#     return values

FACTOR = 10000

def value_key(value):
    if value[0] >= FACTOR or value[1] >= FACTOR or value[2] >= FACTOR or value[3] >= FACTOR:
        raise ValueError(value)
    return FACTOR * value[0] + value[1], FACTOR * value[2] + value[3]

def graph_values(graph, vectors, length):
    paths = find_all_paths(graph, length)
    return graph_values1(paths, vectors)

@profile
def graph_values1(paths, vectors):
    values = []
    unique_keys = defaultdict(set)
    for path in paths:
        value = path_value(vectors, path)
        key1, key2 = value_key(value)
        if not key1 in unique_keys or not key2 in unique_keys[key1]:
            values.append(TAU3 @ path_value(vectors, path))
            unique_keys[key1].add(key2)
    return values

@profile
def graph_diff_values1(paths, vectors):
    values = []
    tau3_values = {}
    unique_keys = defaultdict(set)
    for path in paths:
        value = path_value(vectors, path)
        key1, key2 = value_key(value)
        if not key1 in unique_keys or not key2 in unique_keys[key1]:
            value = path_value(vectors, path)
            values.append(value)
            unique_keys[key1].add(key2)
            if not key1 in tau3_values:
                tau3_values[key1] = {}
            tau3_values[key1][key2] = TAU3 @ value
    diff_values = []
    diff_unique_keys = defaultdict(set)
    total = 0
    for i, value1 in enumerate(values):
        for value2 in values[i:]:
            total += 1
            value = value1 - value2
            key1, key2 = value_key(value)
            if not key1 in diff_unique_keys or not key2 in diff_unique_keys[key1]:
                key11, key12 = value_key(value1)
                tau3_value1 = tau3_values[key11][key12]
                key21, key22 = value_key(value2)
                tau3_value2 = tau3_values[key21][key22]
                diff_values.append(tau3_value1 - tau3_value2)
                diff_unique_keys[key1].add(key2)
    print('paths', len(paths), 'values', len(values), 'total', total, 'diff_values', len(diff_values))
    return diff_values

# def max_node_comp_value(graph, vectors, start, length):
#     values = node_values(graph, vectors, start, length)
#     max_comp_value = None
#     for value in values:
#         comp_value = abs(TAU3 @ value)
#         if max_comp_value is None or comp_value > max_comp_value:
#             max_comp_value = comp_value 
#     return max_comp_value

# def max_comp_value(graph, vectors, length):
#     values = graph_values(graph, vectors, length)
#     max_comp_value = None
#     sel_value = None
#     for value in values:
#         comp_value = abs(TAU3 @ value)
#         if max_comp_value is None or comp_value > max_comp_value:
#             max_comp_value = comp_value 
#             sel_value = value
#     return max_comp_value, sel_value

def max_comp_value_diff(graph, vectors, length):
    values = graph_values(graph, vectors, length)
    return max_comp_value_diff1(values)

@profile
def max_comp_value_diff1(values):
    max_comp_value = None
    sel_value1, sel_value2 = None, None
    for i, value1 in enumerate(values):
        for value2 in values[i:]:
            comp_value = abs(value1 - value2)
            if max_comp_value is None or comp_value > max_comp_value:
                max_comp_value = comp_value 
                sel_value1 = value1
                sel_value2 = value2
    return max_comp_value, sel_value1, sel_value2

@profile
def max_comp_value_diff2(values):
    max_comp_value = None
    sel_value1 = None
    for value in values[i:]:
        comp_value = abs(value)
        if max_comp_value is None or comp_value > max_comp_value:
            max_comp_value = comp_value 
            sel_value1 = value
    return max_comp_value, sel_value1

graph, vectors = create_graph(GRAPH)
print('graph', graph)
print('vectors', vectors)
#print(TAU3)

#print('l9', len(graph_values(graph, vectors, 9)))
#m9, v1, v2 = max_comp_value_diff(graph, vectors, 9)
#print(m9, v1, v2)
    
sel_i, max_mv, sel_v1, sel_v2 = None, None, None, None
for i in range(1, 18):
    cis = ((abs(lam_2)**i)*0.81582)/(1 - abs(lam_2))
    paths = find_all_paths(graph, i)
    values = graph_values1(paths, vectors)
    mv, v1, v2 = max_comp_value_diff1(values)
    print(i, mv, v1 - v2, mv + cis)
    if max_mv is None or mv > max_mv:
        max_mv = mv
        sel_v1 = v1
        sel_v2 = v2
        sel_i = i
print('MAX', sel_i, max_mv, sel_v1, sel_v2)
print_prof_data()
 
clear_prof_data()

sel_i, max_mv, sel_v1, sel_v2 = None, None, None, None
for i in range(1, 16):
    cis = ((abs(lam_2)**i)*0.81582)/(1 - abs(lam_2))
    paths = find_all_paths(graph, i)
    values = graph_diff_values1(paths, vectors)
    mv, v1 = max_comp_value_diff2(values)
    print(i, mv, v1, mv + cis)
    if max_mv is None or mv > max_mv:
        max_mv = mv
        sel_v1 = v1
        sel_i = i
print('MAX', sel_i, max_mv, sel_v1)
print_prof_data()

# graph defaultdict(<class 'set'>, {0: {0, 1}, 1: {2}, 2: {1, 3}, 3: {0, 2}})
# vectors {0: array([0, 0, 0, 0]), 1: array([1, 0, 0, 0]), 32: array([1, 0, 0, 0]), 21: array([0, 0, 0, 1]), 23: array([0, 0, 0, 0]), 12: array([0, 0, 0, 0]), 30: array([0, 0, 0, 0])}
# 1 0.815820667327 (-0.578802175158+0.574935999281j) 2.18696925457
# 2 0.989529789598 (0.67597055164+0.722656915706j) 1.84918934725
# 3 0.967096437913 (0.0794223724614+0.963829656618j) 1.50607125212
# 4 1.00534542714 (-0.354031388227-0.940946971945j) 1.34326274308
# 5 1.02412560275 (0.503353723696-0.891890284202j) 1.23598728795
# 6 1.02412560275 (0.503353723696-0.891890284202j) 1.15695505995
# 7 1.05829383149 (0.488073989169-0.939025886148j) 1.14157299866
# 8 1.0484530504 (0.715352857289-0.766501199254j) 1.10066601453
# 9 1.0551720669 (-0.519592076211+0.918374741106j) 1.08790766833
# 10 1.05756228319 (-0.51030113601+0.926299483657j) 1.07808629708
# 11 1.05756228319 (-0.51030113601+0.926299483657j) 1.0704300824
# 12 1.05433032913 (-0.510981394148+0.92223123877j) 1.06239796431
# 13 1.05536853257 (0.513954799267-0.921766349925j) 1.06042664207
# 14 1.05629085008 (0.512965007834-0.923372763683j) 1.05946209805
# 15 1.05629085008 (0.512965007834-0.923372763683j) 1.05827910551
# 16 1.05570853444 (0.512280718878-0.923086656141j) 1.05695509721
# 17 1.05572684828 (-0.512695841631+0.922877105665j) 1.05650839713
# MAX 7 1.05829383149 (0.563522440632-0.622071601227j) (0.0754484514626+0.316954284921j)
# Function find_all_paths called 17 times.
# Execution time max: 0.162, average: 0.020
# Function graph_values1 called 17 times.
# Execution time max: 1.327, average: 0.178
# Function max_comp_value_diff1 called 17 times.
# Execution time max: 31.671, average: 2.870




