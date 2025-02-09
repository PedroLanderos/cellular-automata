#This exercise works with recurrence equations, which are expressions where the next term depends on previous ones.

#the given ecuation is: Xn+1 = 2(x) + 3

def DiscreteSequence(n):
    #base case
    x = 1

    #list to store the x values 
    result = []

    for i in range (n - 1):
        x = 2*x + 3
        result.append(x)

    return result

#example with n = 10 
print(DiscreteSequence(10))

