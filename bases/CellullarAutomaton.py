#automata rule 30 is a class 3 rule that follows simple well defined rules 


import numpy as np

def CellullarAutomataRule30(steps, size=21): #defines the size 21 as an odd number
    #list of zeros 
    state = np.zeros(size, dtype=int)
    #start the central cell with "1"
    state[size // 2] = 1

    for i in range(steps):
        print("".join(["█" if x else " " for x in state])) 
        newState = np.zeros_like(state)

        for j in range(1, size - 1):
            left, center, right = state[j - 1], state[j], state[j + 1]

            #pre defined conditions 
            if (left, center, right) in [(1, 1, 1), (0, 0, 0)]:  
                newState[j] = 0
            else:
                newState[j] = 1
        
        state = newState


CellullarAutomataRule30(10)
            
            