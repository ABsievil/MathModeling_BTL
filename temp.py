import numpy as np
from gamspy import Model, Container, Set, Parameter, Variable, Equation

# Set up the model
n = 8
m = 5
S = 2
ps = 1/2
MAX_VALUE = 100
c = np.random.randint(0, MAX_VALUE + 1, m)
l = np.random.randint(0, MAX_VALUE + 1, n)
q = np.random.randint(0, MAX_VALUE + 1, n)
s = np.random.randint(0, MAX_VALUE + 1, m)
A = np.random.randint(0, MAX_VALUE + 1, size=(n, m))
D = np.random.binomial(10, 0.5, n)
D[D < 0] = 0
"""
D = [np.random.binomial(10, 0.5, n) for _ in range(S)]
D = [np.clip(arr, a_min=0, a_max=None) for arr in D]
"""

print("c: ",c)
print("l: ",l)
print("q: ",q)
print("s: ",s)
print("D: ",D)
print("A: \n",A)

#====================
# Create GAMS model
container = Container(delayed_execution=True)
model_name = "MyModel"
problem_type = "MIN"

# Define sets
c_set = Set(container, name = "c_set", records= c)
l_set = Set(container, name = "l_set", records= l)
q_set = Set(container, name = "q_set", records= q)
s_set = Set(container, name = "s_set", records= s)
D_set = Set(container, name = "D_set", records= D)

A_tranpose = A.T
A_list = A_tranpose.tolist()
A_row = [row[0] for row in A_list]
A_set = Set(container, name = "A_set", records= A_row)

# Define parameters
c_param = Parameter(container, "c", domain=c_set)
l_param = Parameter(container, "l", domain=l_set)
q_param = Parameter(container, "q", domain=q_set)
s_param = Parameter(container, "s", domain=s_set)
D_param = Parameter(container, "D", domain=D_set)
A_param  = Parameter(container, "A", domain = [A_set, A_set, A_set, A_set], records= A_list)

# Define variables
x_var = Variable(container, name= "x")
y_var = Variable(container, name= "y")
z_var = Variable(container, name= "z")
of = Variable(container, name="ofjective")

# Define equations for variables
x_contrain = Equation(container, "x_contrain", type="regular")
y_contrain = Equation(container, "y_contrain", type="regular")
z_contrain = Equation(container, "z_contrain", type="regular")
of_contrain = Equation(container, "objective_contrain", type="regular")
x_contrain[...] =  x_var >= 0
y_contrain[...] =  (y_var == x_var - np.dot(A_param.T, z_var)) & (y_var >= 0)
z_contrain[...] =  0 <= z_var <= D_param
of_contrain[...] = np.dot(c_param.T, x_var) + np.dot((l_param - q_param).T, z_var) - np.dot(s_param.T, y_var)

"""
# Define variables

x = {i: Variable(container, name=f"x_{i}", type="integer") for i in range(m)}
y = {i: Variable(container, name=f"y_{i}", type="integer") for i in range(m)}
z = {i: Variable(container, name=f"z_{i}", type="integer") for i in range(n)}
of = Variable(container, name="objective")

# Define equations for variables
x_contrain = [Equation(container, f"x_contrain{i}", type="regular") for i in range(m)]
y_contrain = [Equation(container, f"y_contrain{i}", type="regular") for i in range(m)]
z_contrain = [Equation(container, f"z_contrain{i}", type="regular") for i in range(n)]
of_contrain = Equation(container, "objective_contrain", type="regular")

for i in range(m):
    x_contrain[i][...] = x[i] >= 0                                  # x >=0 

for i in range(n):
    z_contrain[i][...] = (0 <= z[i]) & (z[i] <= int(D[i]))          # 0 <= z <= D

for j in range(m):
    sum_expr = sum(A[i][j] * z[i] for i in range(n))
    y_contrain[j][...] = ( y[j] == x[j] - sum_expr ) & (y[j] >=0)   # y= x - A.T * z

one_stage = sum(c[i] * x[i] for i in range(m))                      # c.T * x
two_stage_first = sum((l[i] - q[i])*z[i] for i in range(n))         #(l - q).T * z
two_stage_second = sum(s[j] * y[j] for j in range(m))               # s.T * y
of_contrain[...] = of ==  one_stage + 1/2*(two_stage_first - two_stage_second)
"""

# Solve the model with parameters
model = Model(
    container,
    name="LP",
    equations=container.getEquations(),
    problem="LP",
    sense="MIN",
    objective=of,
)
model.solve()

# Print the results
print("Objective Function Value:  ", round(of.toValue(), 4), "\n")
print("x:  ", round(x_var.toValue(), 4))
print("y:  ", round(y_var.toValue(), 4))
print("z:  ", round(z_var.toValue(), 4))



# Save the GAMS model
#model.export("2SLPWR_Model.gms")