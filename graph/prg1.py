from numpy import dot
from numpy import linalg as LA
from numpy import array

#konstanty hornich mezi
C1 = 1.903191 
C2 = 2.981814
C3 = 2.113017
C4 = 2.113017
# C3old =  2.175816
# C4old =  2.175816

TAU1 =  [0.5124 , 0.5979 , 0.3537 , 0.6569]
TAU2 = [ 0.1806 , 0.6809 , -0.4524 , -0.5724]
TAU3 = [ 0.5788 - 0.5749j , -0.3219 +0.2183j ,-0.0690 + 0.6165j , -0.1662 - 0.6810j]
TAU4 = [0.5788 + 0.5749j , -0.3219 -0.2183j ,-0.0690 -0.6165j , -0.1662 +0.6810j]

M = array([[1, 0, 0, 1], [0, 0, 1, 1], [1, 1, 0, 0], [0, 1, 0, 0]])

#tyhle tri vektory jsou labely hran v nasem malem grafu
V1 = array([0, 0, 0, 0]) 
V2 = array([1, 0, 0, 0])
V3 = array([0, 0, 0, 1])

GRAPH = {(0,0): V1, (0,1): V2, (1, 2): V1, (2, 1): V3, (2, 3): V1, (3, 2): V2, (3, 0): V1}
GRAPH_K = GRAPH.keys()

POC = [-7, -7, -7, -7]

#zkontroluje, zda je TAU_i(v) mensi nez predepsane konstanty
def zkontroluj(vek): 
    if abs(dot( TAU1, vek)) <= C1:
        if abs(dot( TAU2, vek)) <= C2:
            if abs(dot( TAU3, vek)) <= C3:
                if abs(dot( TAU4, vek)) <= C4:
                    return True
    return False

def vytvor_vektory():
    vektory = []
    for i1 in range(0, 14):
        for i2 in range(0, 14):
            for i3 in range(0, 14):
                for i4 in range(0, 14):
                    vek = [POC[0] + i1, POC[1] + i2, POC[2] + i3, POC[3] + i4]
                    if LA.norm(vek) <= 6.28:
                        if zkontroluj(vek):
                            vektory.append(vek)  
    return vektory                
    
# priklad multivrcholu
# a1 = [[0, 0, 2, 3], [0,0,0,0], [1,1,1,1]] 
# a2 = [[0, 1, 0, 2], [0,0,0,0], [1,1,1,1]]

#zkontroluje, zda mezi kazdym vrcholem z a1 vede hrana do vrcholu a2 v grafu Q
def sedi_hrany(a1, a2):
    for i in range(0,4):
        if not (a1[0][i], a2[0][i]) in GRAPH_K:
            return False
    return True

#zkontroluje, jestli pro zadanou dvojici vrcholu bude mozne vest hranu
def sedi_vektory(a1, a2): 
    l1 = GRAPH[(a1[0][0], a2[0][0])]
    l2 = GRAPH[(a1[0][1], a2[0][1])]
    l3 = GRAPH[(a1[0][2], a2[0][2])]
    l4 = GRAPH[(a1[0][3], a2[0][3])]
    if not a2[1] == M.dot(a1[1]) + l3 - 2*l2 + l1:
        return False
    if not a2[2] == M.dot(a1[2]) + l4 - 2*l3 + l2:
        return False
    return True

#v grafu,ktery tvorim (graf G), povede hrana z a1 do a2 tehdy a jen tehdy, pokud sedi_hrany a zaroven sedi_vektory

def vytvor_vrcholy(vektory): #vytvori vsechny vrcholy grafu G
    vrcholy = []
    for i1 in [0, 1, 2, 3]:
        for i2 in [0, 1, 2, 3]:
            for i3 in [0, 1, 2, 3]:
                for i4 in [0, 1, 2, 3]:
                    for u in vektory:
                        for v in vektory:
                            vrchol = [[i1, i2, i3, i4], u, v]
                            vrcholy.append(vrchol)
    return vrcholy                     
                   

 
# 465
vektory =  vytvor_vektory()
print(len(vektory))
# 55353600
vrcholy = vytvor_vrcholy(vektory)
print(vrcholy)
