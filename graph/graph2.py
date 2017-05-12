from numpy import array, linalg
from collections import defaultdict

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

def totuple(a):
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a

def find_vectors(graph, vectors, start, length):
    if length == 0:
        return []
    paths = [get_vector(start, _next) + path for _next in graph[start] for path in find_paths(graph, _next, length - 1)]
    return paths

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

def node_values(graph, vectors, length):
    values = set()
    for node in graph:
        paths = find_paths(graph, node, length)
        for path in paths:
            pomoc = totuple(path_value(vectors, path))
            values.add(pomoc)
    return(values)

def max_comp_value_diff(graph, vectors, length):
    values = node_values(graph, vectors, length)
    max_comp_value = None
    sel_value1, sel_value2 = None, None
    for value1 in values:
        for value2 in values:
            arr = array([value1[0] - value2[0],value1[1] - value2[1],value1[2] - value2[2],value1[3] - value2[3]])
            comp_value = abs(TAU3 @ arr)
            if max_comp_value is None or comp_value > max_comp_value:
                max_comp_value = comp_value 
                sel_value1 = value1
                sel_value2 = value2
    return max_comp_value, sel_value1, sel_value2

print(L[2])


graph, vectors = create_graph(GRAPH)
print(graph)
print(vectors)

print(TAU3)
minim = 0.

node_values(graph, vectors, 3)

for i in range(1,16):
    cis = ((abs(lam_2)**i)*0.81582)/(1 - abs(lam_2))
    m9, v1, v2 = max_comp_value_diff(graph, vectors, i)
    print(i, ' :' , m9, v1, v2, cis, 'celkem to dava: ', m9 + cis)
    if minim == 0. or m9 < minim:
        minim = m9
          
print(minim)
