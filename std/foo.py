#!/usr/bin/python3 
# this is a reference

import random
import os
import time

def listtostr(x):
    s = ''

    for i in range(len(x)):
        if x[i] == 1:
            s += '*'
        else:
            s += ' '

    return(s)

def rule110(x, y, z):
    if x == 1 and y == 1 and z == 1:
        return(0)
    elif x == 1 and y == 1 and z == 0:
        return(1)
    elif x == 1 and y == 0 and z == 1:
        return(1)
    elif x == 1 and y == 0 and z == 0:
        return(0)
    elif x == 0 and y == 1 and z == 1:
        return(1)
    elif x == 0 and y == 1 and z == 0:
        return(1)
    elif x == 0 and y == 0 and z == 1:
        return(1)
    elif x == 0 and y == 0 and z == 0:
        return(0)

rows, columns = os.popen('stty size', 'r').read().split()

l = []
l2 = []

for i in range(int(columns)):
    l.append(random.randint(0, 1))
    
print('\n' + listtostr(l))

while True:
    for i in range(len(l) - 1):
        l2.append(rule110(l[i -1], l[i], l[i + 1]))

    l2.append(rule110(l[len(l) - 2], l[len(l) - 1], l[0]))

    print(listtostr(l2))

    l = l2
    l2 = []
    
    time.sleep(.03)
