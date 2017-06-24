from numpy import dot, array, empty
from numpy import linalg as LA
import numpy
from datetime import datetime

C1 = 1.903191
C2 = 2.981814
C3 = 2.112533
C4 = 2.112533
# C3old =  2.175816
# C4old =  2.175816

TAU1 =  [0.5124 , 0.5979 , 0.3537 , 0.6569]
TAU2 = [ 0.1806 , 0.6809 , -0.4524 , -0.5724]
TAU3 = [ 0.5788 - 0.5749j , -0.3219 +0.2183j ,-0.0690 + 0.6165j , -0.1662 - 0.6810j]
TAU4 = [0.5788 + 0.5749j , -0.3219 -0.2183j ,-0.0690 -0.6165j , -0.1662 +0.6810j]

M = array([[1, 0, 0, 1], [0, 0, 1, 1], [1, 1, 0, 0], [0, 1, 0, 0]])
ABCD = [0, 1, 5, 8]


#tyhle tri vektory jsou labely hran v nasem malem grafu
V1 = array([0, 0, 0, 0])
V2 = array([1, 0, 0, 0])
V3 = array([0, 0, 0, 1])

GRAPH = {(0,0): V1, (0,1): V2, (1, 2): V1, (2, 1): V3, (2, 3): V1, (3, 2): V2, (3, 0): V1}
GRAPH_K = GRAPH.keys()

DETI = [[0, 1], [2], [1, 3], [2, 0]]

POC = [-7, -7, -7, -7]

X = [[[0, 0, 0, 1], array([ 0, 0, 0,  0]), array([ 1, 0, 0,  0])],
     [[0, 0, 1, 1], array([ 1, 0, 0,  0]), array([-1, 0, 0,  0])],
     [[0, 1, 1, 1], array([-1, 0, 0,  0]), array([ 0, 0, 0,  0])], 
     [[3, 3, 3, 1], array([ 0, 0, 0,  0]), array([ 0, 0, 0,  1])],
     [[3, 3, 1, 1], array([ 0, 0, 0,  1]), array([ 0, 0, 0, -1])],
     [[3, 1, 1, 1], array([ 0, 0, 0, -1]), array([ 0, 0, 0,  0])],
     [[0, 0, 0, 2], array([ 0, 0, 0,  0]), array([ 1, 0, 0,  0])],
     [[0, 0, 2, 2], array([ 1, 0, 0,  0]), array([-1, 0, 0,  0])],
     [[0, 2, 2, 2], array([-1, 0, 0,  0]), array([ 0, 0, 0,  0])]
    ]

#zkontroluje, zda je TAU_i(v) mensi nez predepsane konstanty
def zkontroluj_tau(vek):
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
                    vek = array([POC[0] + i1, POC[1] + i2, POC[2] + i3, POC[3] + i4])
                    if LA.norm(vek) <= 6.28:
                        if zkontroluj_tau(vek):
                            vektory.append(vek)
    print('pocet_vektoru', len(vektory))
    return vektory

def neni_treti_mocnina(a1):
    if a1[1][0] + a1[1][1] + a1[1][2] + a1[1][3] == 0:
        if a1[1][0] * ABCD[0] + a1[1][1] * ABCD[1] + a1[1][2] * ABCD[2] + a1[1][3] * ABCD[3] == 0:
            if a1[2][0] + a1[2][1] + a1[2][2] + a1[2][3] == 0:
                if a1[2][0] * ABCD[0] + a1[2][1] * ABCD[1] + a1[2][2] * ABCD[2] + a1[2][3] * ABCD[3] == 0:
                    return False
    return True

def podej_hash(v):
    i_hash = 4 * 4 * 4 * v[0][0] + 4 * 4 * v[0][1] + 4 * v[0][2] + v[0][3]
    u_hash = 9 * 9 * 9 * (v[1][0] + 4) + 9 * 9 * (v[1][1] + 4) + 9 * (v[1][2] + 4) + v[1][3]
    v_hash = 9 * 9 * 9 * (v[2][0] + 4) + 9 * 9 * (v[2][1] + 4) + 9 * (v[2][2] + 4) + v[2][3]
    _hash = u_hash * (4 * 4 * 4 * 4 * 9 * 9 * 9 * 9) + v_hash * (4 * 4 * 4 * 4) + i_hash
    return _hash

def podej_hash2(v):
    i_hash = 4 * v[0][0] + v[0][1]
    u_hash = 9 * 9 * 9 * (v[1][0] + 4) + 9 * 9 * (v[1][1] + 4) + 9 * (v[1][2] + 4) + v[1][3]
    v_hash = 9 * 9 * 9 * (v[2][0] + 4) + 9 * 9 * (v[2][1] + 4) + 9 * (v[2][2] + 4) + v[2][3]
    _hash = u_hash * (4 * 4 * 9 * 9 * 9 * 9) + v_hash * (4 * 4) + i_hash
    return _hash

class Potomci:
    def __init__(self):
        self.potomci = []
        for _ in range(16):
            self.potomci.append({})

    def existuje_pridej(self, v):
        ix = 4 * v[0][2] + v[0][3]
        _potomci = self.potomci[ix]
        _hash = podej_hash2(v)
        if _hash in _potomci:
            return True
        _potomci[_hash] = v
        return False

    def pridej(self, v):
        ix = 4 * v[0][2] + v[0][3]
        _potomci = self.potomci[ix]
        _hash = podej_hash2(v)
        _potomci[_hash] = v

def najdi_potomky(a1):
    potomci = []
    for i1 in DETI[a1[0][0]]:
        for i2 in DETI[a1[0][1]]:
            for i3 in DETI[a1[0][2]]:
                for i4 in DETI[a1[0][3]]:
                    hod = [i1, i2, i3, i4]
                    label = [GRAPH[(a1[0][0], hod[0])],GRAPH[(a1[0][1], hod[1])], GRAPH[(a1[0][2], hod[2])], GRAPH[(a1[0][3], hod[3])]]
                    u = M.dot(a1[1]) + label[2] - 2*label[1] + label[0]
                    v = M.dot(a1[2]) + label[3] - 2*label[2] + label[1]
                    if zkontroluj_tau(u):
                        if zkontroluj_tau(v):
                            if zkontroluj_tau(u + v):
                                potomci.append([[i1, i2, i3, i4], u, v])
    return potomci

def over_x(x, seznam_poctu):
    print(x)
    opakujici_potomci = Potomci()
    potomci = najdi_potomky(x)
    for p in potomci:
        opakujici_potomci.pridej(p)
    pocet_potomku = len(potomci)
    ix = 0
    while pocet_potomku > 0:
        dalsi_potomci = []
        for p in potomci:
            if not neni_treti_mocnina(p):
                raise ValueError('treti mocnina', x, p)
            for pp in najdi_potomky(p):
                if opakujici_potomci.existuje_pridej(pp):
                    continue
                dalsi_potomci.append(pp)
        potomci = dalsi_potomci
        pocet_potomku = len(potomci)
        ix += 1
        print(ix, pocet_potomku)
        seznam_poctu.append(pocet_potomku)
        if ix >= 50:
            break;
    print('potomci', len(potomci))
    return len(potomci)
      
def over_xx(seznam_poctu):
    for x in X:
        if over_x(x, seznam_poctu) > 0:
            return False
    return True
 
def main():
    print(str(datetime.now()))
    seznam_poctu = []
    tremoc = over_xx(seznam_poctu)
    if tremoc:
        print('Gratulujeme')
    print(str(datetime.now()))

if __name__ == '__main__':
    main()

