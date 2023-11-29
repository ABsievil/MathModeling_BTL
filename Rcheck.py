import numpy as np
from gamspy import Sum, Model, Container, Set, Parameter, Variable, Equation, Sense
import sys

# Set up the model
n = 8
m = 5
S = 2
ps = 1/2
MAX_VALUE = 50

# Random values for vectors and matrices
l_arr = np.random.randint(0, MAX_VALUE, n)
q_arr = l_arr + np.random.randint(1, MAX_VALUE, n)

s_arr = np.random.randint(0, MAX_VALUE, m)
c_arr = s_arr + np.random.randint(1, MAX_VALUE, m)

A_arr = np.random.randint(0, MAX_VALUE, size=(n, m))

D_arr1 = np.random.binomial(10, 0.5, n)
D_arr2 = np.random.binomial(10, 0.5, n)
D_arr1[D_arr1 <= 0] = 0
D_arr2[D_arr2 <= 0] = 0
"""
D_arr = [np.random.binomial(10, 0.5, n) for _ in range(S)]
D_arr = [np.clip(arr, a_min=0, a_max=None) for arr in D_arr]
"""

print("l: ", l_arr)
print("Size of 1D l_arr:", len(l_arr))
print("q: ", q_arr)
print("Size of 1D q_arr:", len(q_arr))
print("s: ", s_arr)
print("Size of 1D s_arr:", len(s_arr))
print("c: ", c_arr)
print("Size of 1D c_arr:", len(c_arr))
print("A: \n", A_arr)
rows = len(A_arr)
columns = len(A_arr[0])
print("Number of rows A_arr:", rows)
print("Number of columns A_arr:", columns)
print("D1: ", D_arr1)
print("Size of 1D D_arr1:", len(D_arr1))
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
A_tranpose = A_arr.T
A_record = [["j"+ str(j), "i"+ str(i), A_tranpose[j][i]] for j in range(m) for i in range(n) ]
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
A = Parameter(container, "A", domain = [j ,i], records = A_record)
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
y1_contrain = Equation(container, name = "y1_contrain", type="regular", domain = [j])
z1_contrain = Equation(container, name = "z1_contrain", type="regular", domain = [i])

y2_positive = Equation(container, name = "y2_positive", type="regular", domain = [j])
z2_positive = Equation(container, name = "z2_positive", type="regular", domain = [i])
y2_contrain = Equation(container, name = "y2_contrain", type="regular", domain = [j])
z2_contrain = Equation(container, name = "z2_contrain", type="regular", domain = [i])

# Build contrains for variables
x_positive[j] = x[j] >=0 and x[j] <= 5*MAX_VALUE            # x[j] >=0 && x[j] <= 500
y1_positive[j] = y1[j] >=0                                  # y1[j] >=0 
z1_positive[i] = z1[i] >=0                                  # z1[i] >=0 
z1_contrain[i] = z1[i] <= D1[i]                             # z1[i] <= D1[i]
y1_contrain[j] = y1[j] == Sum(i, x[j] - A[j, i]*z1[i])      # y1[j] = x[j] - A[i, j]*z1[i]

y2_positive[j] = y2[j] >=0                                  # same
z2_positive[i] = z2[i] >=0                                  # same
z2_contrain[i] = z2[i] <= D2[i]                             # same
y2_contrain[j] = y2[j] == Sum(i, x[j] - A[j, i]*z2[i])      # same

# build module for objection function value
"""
oneStage = Sum(j, c[j]*x[j])                                # calculate c[j]*x[j]
twoStage_step1_sce1 = Sum(i, (l[i] - q[i])*z1[i])           # calculate (l[i] - q[i])*z1[i]
twoStage_step2_sce1 = Sum(j, s[j]*y1[j])                    # calculate s[j]*y1[j]

twoStage_step1_sce2 = Sum(i, (l[i] - q[i])*z2[i])           # calculate (l[i] - q[i])*z2[i]
twoStage_step2_sce2 = Sum(j, s[j]*y2[j])                    # calculate s[j]*y2[j]
obj =  oneStage + ps*(twoStage_step1_sce1 - twoStage_step2_sce1) + ps*(twoStage_step1_sce2 - twoStage_step2_sce2)
"""
obj = Sum(j, c[j]*x[j]) + ps*( Sum(i, (l[i] - q[i])*z1[i]) - Sum(j, s[j]*y1[j]) ) + ps*( Sum(i, (l[i] - q[i])*z2[i]) - Sum(j, s[j]*y2[j]) )
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
model.solve(output=sys.stdout) 
#model.solve()

# Print the results
print("Objective Function Value:  ", model.objective_value)
print("records x: ", x.records, sep="\n")
print("records y1: ", y1.records, sep="\n")
print("records y2: ", y2.records, sep="\n")
print("records z1: ", z1.records, sep="\n")
print("records z2: ", z2.records, sep="\n")

# redirect output to a file
with open("my_out_file", "w") as file:
    model.solve(output=file)