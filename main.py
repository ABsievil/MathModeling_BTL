import sys
import numpy as np
from gamspy import Sum, Model, Container, Set, Parameter, Variable, Equation, Sense

# Set up the model
n = 8
m = 5
S = 2
ps = 1/2
MAX_VALUE = 50

# Random values for vectors and matrices
l_arr = np.random.randint(1, MAX_VALUE, n)
q_arr = l_arr + np.random.randint(1, MAX_VALUE, n)

s_arr = np.random.randint(1, MAX_VALUE, m)
c_arr = s_arr + np.random.randint(1, MAX_VALUE, m)

A_arr = np.random.randint(1, MAX_VALUE, size=(n, m))

D_arr1 = np.random.binomial(10, 0.5, n)
D_arr2 = np.random.binomial(10, 0.5, n)

"""
l_arr = [15, 29, 42, 15, 17, 27, 32, 31]
q_arr = [45, 68, 87, 58, 45, 48, 38, 48]
s_arr = [ 5, 10, 8, 39, 10]
c_arr = [ 9, 37, 44, 76, 27]
A_arr = [[15, 8, 17, 22, 21],
        [42, 45, 4, 10, 23],
        [ 8, 6, 49, 49, 47],
        [ 5, 31, 38, 20, 38],
        [ 0,  3, 10, 43,  8],
        [13, 30, 23, 33,  3],
        [33,  8,  1,  9, 41],
        [23, 26, 29, 34, 38]]
D_arr1 = [6, 6, 6, 5, 3, 3, 3, 6]
D_arr2 = [9, 8, 4, 3, 6, 6, 5, 5]

D_arr = [np.random.binomial(10, 0.5, n) for _ in range(S)]
D_arr = [np.clip(arr, a_min=0, a_max=None) for arr in D_arr]
"""

print("l: ", l_arr)
print("q: ", q_arr)
print("s: ", s_arr)
print("c: ", c_arr)
A_temp = np.array(A_arr)
print("A: \n", A_arr)
print("D1: ", D_arr1)
print("D2: ", D_arr2)

#====================
# Create Container for GAMS model
container = Container(delayed_execution=True)

# Define sets
i = Set(container, "i", records= ["i" + str(i) for i in range(n)])
j = Set(container, "j", records= ["j" + str(j) for j in range(m)])

# Define records for parameters
l_record = [["i"+ str(i), l_arr[i]] for i in range(n)]
q_record = [["i"+ str(i), q_arr[i]] for i in range(n)]
s_record = [["j"+ str(j), s_arr[j]] for j in range(m)]
c_record = [["j"+ str(j), c_arr[j]] for j in range(m)]
A_record = [["i"+ str(i), "j"+ str(j), A_arr[i][j]] for i in range(n) for j in range(m)]
D_record1 = [["i"+ str(i), D_arr1[i]] for i in range(n)]
D_record2 = [["i"+ str(i), D_arr2[i]] for i in range(n)]

"""
print("l_record", l_record)
print("q_record", q_record)
print("s_record", s_record)
print("c_record", c_record)
print("A_record", A_record)
print("D_record 1", D_record1)
print("D_record 2", D_record2)
"""
# Define parameters
l = Parameter(container, "l", domain = [i], records = l_record)
q = Parameter(container, "q", domain = [i], records = q_record)
s = Parameter(container, "s", domain = [j], records = s_record)
c = Parameter(container, "c", domain = [j], records = c_record)
A = Parameter(container, "A", domain = [i, j], records = A_record)
D1 = Parameter(container, "D1", domain = [i], records = D_record1)
D2 = Parameter(container, "D2", domain = [i], records = D_record2)

# Define variables
x = Variable(container, name= "x", domain = [j], type = "Positive")
y1 = Variable(container, name= "y1", domain = [j], type = "Positive")
z1 = Variable(container, name= "z1", domain = [i], type = "Positive")
y2 = Variable(container, name= "y2", domain = [j], type = "Positive")
z2 = Variable(container, name= "z2", domain = [i], type = "Positive")

# Define equations for variables
x_positive = Equation(container, name = "x_positive", type="regular", domain = [j])
y1_positive = Equation(container, name = "y1_positive", type="regular", domain = [j])
z1_positive = Equation(container, name = "z1_positive", type="regular", domain = [i])
y1_contraint = Equation(container, name = "y1_contraint", type="regular", domain = [j])
z1_contraint = Equation(container, name = "z1_contraint", type="regular", domain = [i])

y2_positive = Equation(container, name = "y2_positive", type="regular", domain = [j])
z2_positive = Equation(container, name = "z2_positive", type="regular", domain = [i])
y2_contraint = Equation(container, name = "y2_contraint", type="regular", domain = [j])
z2_contraint = Equation(container, name = "z2_contraint", type="regular", domain = [i])

# Build contraints for variables
x_positive[j] = x[j] >=0 and x[j] <= 5*MAX_VALUE            # x[j] >=0 && x[j] <= 500
y1_positive[j] = y1[j] >=0                                  # y1[j] >=0 
z1_positive[i] = z1[i] >=0                                  # z1[i] >=0 
z1_contraint[i] = z1[i] <= D1[i]                            # z1[i] <= D1[i]
y1_contraint[j] = y1[j] == Sum(i, x[j] - A[i, j]*z1[i])     # y1[j] = x[j] - A[i, j]*z1[i]

y2_positive[j] = y2[j] >=0                                  # y2[j] >=0 
z2_positive[i] = z2[i] >=0                                  # z2[i] >=0 
z2_contraint[i] = z2[i] <= D2[i]                            # z2[i] <= D2[i]
y2_contraint[j] = y2[j] == Sum(i, x[j] - A[i, j]*z2[i])     # y2[j] = x[j] - A[i, j]*z2[i]

# build module for objection function value
firstStage = Sum(j, c[j]*x[j])                              # calculate c[j]*x[j]

secondStage_step1_sce1 = Sum(i, (l[i] - q[i])*z1[i])        # calculate (l[i] - q[i])*z1[i]
secondStage_step2_sce1 = Sum(j, s[j]*y1[j])                 # calculate s[j]*y1[j]

secondStage_step1_sce2 = Sum(i, (l[i] - q[i])*z2[i])        # calculate (l[i] - q[i])*z2[i]
secondStage_step2_sce2 = Sum(j, s[j]*y2[j])                 # calculate s[j]*y2[j]

obj =  firstStage + ps*(secondStage_step1_sce1 - secondStage_step2_sce1) + ps*(secondStage_step1_sce2 - secondStage_step2_sce2)

#obj = Sum(j, c[j]*x[j]) + ps*( Sum(i, (l[i] - q[i])*z1[i]) - Sum(j, s[j]*y1[j]) ) + ps*( Sum(i, (l[i] - q[i])*z2[i]) - Sum(j, s[j]*y2[j]) )
#c[j]*x[j] + ps*( ((l[i] - q[i])*z[i]) - (s[j]*y[j]) )  

# Solve the model with parameters
model = Model(
    container,
    name="myModel",
    equations=container.getEquations(),
    problem="LP",
    sense=Sense.MIN,
    objective=obj,
)
#model.solve(output=sys.stdout) 
model.solve()

# Print the results
print("====================================")
print("Result: ")
print("x: ", list(map(int, x.records['level'].values)))
print("y1: ", list(map(int, y1.records['level'].values)))
print("y2: ", list(map(int, y2.records['level'].values)))
print("z1: ", list(map(int, z1.records['level'].values)))
print("z2: ", list(map(int, z2.records['level'].values)))

print("Objective Function Value: ", model.objective_value)

# redirect output to a file
with open("progress_build_model", "w") as file:
    model.solve(output=file)