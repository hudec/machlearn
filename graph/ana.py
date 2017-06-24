from numpy import *

v = array([1., 2.])
M = array([[1., 2], [3., 4]])

print('v', v)
print('M', M)
c = M @ v
print('c', c)
c2 = v @ M
print('c2', c2)
