import numpy as np
from gamspy import Sum, Model, Container, Set, Parameter, Variable, Equation, Sense

# Set up the model
n = 8
m = 5
S = 2
ps = 1/2
MAX_VALUE = 10

# Random values for vectors and matrices
l_arr = np.random.randint(1, MAX_VALUE, n)
s_arr = np.random.randint(1, MAX_VALUE, m)
q_arr = l_arr + np.random.randint(1000* MAX_VALUE, 2000* MAX_VALUE, n)
c_arr = s_arr + np.random.randint(10* MAX_VALUE, 20* MAX_VALUE, m)
D_arr1 = np.random.binomial(10, 0.5, n)
D_arr2 = np.random.binomial(10, 0.5, n)
A_arr = np.random.randint(1, 10* MAX_VALUE, size=(n, m))

# Print vectors and matrices
print("Values of vectors and matrices:")
print("l: ", l_arr)
print("s: ", s_arr)
print("q: ", q_arr)
print("c: ", c_arr)
print("D1: ", D_arr1)
print("D2: ", D_arr2)
print("A: \n", A_arr)

# Create Container for GAMS model
container = Container(delayed_execution=True)

# Define sets
i = Set(container, "i", records= ["i" + str(i) for i in range(n)])
j = Set(container, "j", records= ["j" + str(j) for j in range(m)])

# Define records for parameters
l_record = [["i" + str(i), l_arr[i]] for i in range(n)]
q_record = [["i" + str(i), q_arr[i]] for i in range(n)]
s_record = [["j" + str(j), s_arr[j]] for j in range(m)]
c_record = [["j" + str(j), c_arr[j]] for j in range(m)]
D_record1 = [["i" + str(i), D_arr1[i]] for i in range(n)]
D_record2 = [["i" + str(i), D_arr2[i]] for i in range(n)]
A_record = [["i" + str(i), "j" + str(j), A_arr[i][j]] for i in range(n) for j in range(m)]

# Define parameters
l = Parameter(container, "l", domain = [i], records = l_record)
q = Parameter(container, "q", domain = [i], records = q_record)
s = Parameter(container, "s", domain = [j], records = s_record)
c = Parameter(container, "c", domain = [j], records = c_record)
D1 = Parameter(container, "D1", domain = [i], records = D_record1)
D2 = Parameter(container, "D2", domain = [i], records = D_record2)
A = Parameter(container, "A", domain = [i, j], records = A_record)

# Define variables
x = Variable(container, name= "x", domain = [j], type = "Positive")
y1 = Variable(container, name= "y1", domain = [j], type = "Positive")
z1 = Variable(container, name= "z1", domain = [i], type = "Positive")
y2 = Variable(container, name= "y2", domain = [j], type = "Positive")
z2 = Variable(container, name= "z2", domain = [i], type = "Positive")

# Define equations for variables
x_positive = Equation(container, name = "x_positive", type="regular", domain = [j])
# Define equations for scenario 1
y1_positive = Equation(container, name = "y1_positive", type="regular", domain = [j])
z1_positive = Equation(container, name = "z1_positive", type="regular", domain = [i])
y1_constraint = Equation(container, name = "y1_constraint", type="regular", domain = [j])
z1_constraint = Equation(container, name = "z1_constraint", type="regular", domain = [i])
# Define equations for scenario 2
y2_positive = Equation(container, name = "y2_positive", type="regular", domain = [j])
z2_positive = Equation(container, name = "z2_positive", type="regular", domain = [i])
y2_constraint = Equation(container, name = "y2_constraint", type="regular", domain = [j])
z2_constraint = Equation(container, name = "z2_constraint", type="regular", domain = [i])

# Build constraints for variables
x_positive[j] = x[j] >=0                                    # x[j] >=0 
# Constraints for scenario 1
y1_positive[j] = y1[j] >=0                                  # y1[j] >=0 
z1_positive[i] = z1[i] >=0                                  # z1[i] >=0 
z1_constraint[i] = z1[i] <= D1[i]                           # z1[i] <= D1[i]
y1_constraint[j] = y1[j] == Sum(i, x[j] - A[i, j]*z1[i])    # y1[j] = x[j] - A[i, j]*z1[i]
# Constraints for scenario 2
y2_positive[j] = y2[j] >=0                                  # y2[j] >=0 
z2_positive[i] = z2[i] >=0                                  # z2[i] >=0 
z2_constraint[i] = z2[i] <= D2[i]                           # z2[i] <= D2[i]
y2_constraint[j] = y2[j] == Sum(i, x[j] - A[i, j]*z2[i])    # y2[j] = x[j] - A[i, j]*z2[i]

# build module for objection function value
firstStage = Sum(j, c[j]*x[j])                              # calculate c[j]*x[j]
# Calculate module for scenario 1
secondStage_step1_sce1 = Sum(i, (l[i] - q[i])*z1[i])        # calculate (l[i] - q[i])*z1[i]
secondStage_step2_sce1 = Sum(j, s[j]*y1[j])                 # calculate s[j]*y1[j]
# Calculate module for scenario 2
secondStage_step1_sce2 = Sum(i, (l[i] - q[i])*z2[i])        # calculate (l[i] - q[i])*z2[i]
secondStage_step2_sce2 = Sum(j, s[j]*y2[j])                 # calculate s[j]*y2[j]

obj =  firstStage + ps*(secondStage_step1_sce1 - secondStage_step2_sce1) + ps*(secondStage_step1_sce2 - secondStage_step2_sce2)

# Solve the model with parameters
model = Model(
    container,
    name="myModel",
    equations=container.getEquations(),
    problem="LP",
    sense=Sense.MIN,
    objective=obj,
)
model.solve()

# Print the results
print("\n====================================")
print("Result: ")
print("x: ", list(map(int, x.records['level'].values)))
print("y1: ", list(map(int, y1.records['level'].values)))
print("y2: ", list(map(int, y2.records['level'].values)))
print("z1: ", list(map(int, z1.records['level'].values)))
print("z2: ", list(map(int, z2.records['level'].values)))

print("Objective Function Value: ", model.objective_value)