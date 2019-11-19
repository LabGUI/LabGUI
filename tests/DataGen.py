"""
Created July 12th

@author: zackorenberg

For generating data to test other stuff
"""


import math
import numpy as np




dat1 = np.array([[0, 0]], dtype='float')

for i in range(300):
    dat1 = np.append(dat1, np.array([[i+1, math.sin(i+1)]]), axis=0)



dat2 = np.array([[0, 0]], dtype='float')

for i in range(20):
    dat2 = np.append(dat2, np.array([[i+290, math.sin(i+290)]]), axis=0)





header = """#C'dt(s)', 'V_DC(V)'
#I'TIME[].dt', 'HP34401A.V_DC'
#P'dt', 'V_DC'
#T'1562869078.2531958'"""

np.savetxt('sdat1.dat', dat1, header=header, comments='')
np.savetxt('sdat2.dat', dat2, header=header, comments='')