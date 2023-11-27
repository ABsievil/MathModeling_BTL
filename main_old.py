import numpy as np
from gamspy import Model, Container, Set, Parameter, Variable, Equation

"""
code with Set and Parameter class
builded at 4:29 pm 26/11/2023
"""
# Set up the model
n = 8
m = 5
S = 2
ps = 1/2
b = np.random.randn(m)
l = np.random.randn(m)
q = np.random.randn(m)
s = np.random.randn(m)
A = np.random.randn(n, m)
D = np.random.binomial(10, 0.5, n)

print("b: ",b)
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
m_set = Set(container=container, name='m_set', domain=[Set(container, f"i_{i}") for i in range(1, m+1)])
n_set = Set(container=container, name='n_set', domain=[Set(container, f"j_{j}") for j in range(1, n+1)])

# Define parameters
b_param = Parameter(container, "b", domain=m_set, records=b)
l_param = Parameter(container, "l", domain=m_set, records=l)
q_param = Parameter(container, "q", domain=m_set, records=q)
s_param = Parameter(container, "s", domain=m_set, records=s)
A_param = Parameter(container, "A", domain=(n_set, m_set), records=A)
D_param = Parameter(container, "D", domain=n_set, records=D)

# Define variables
x = Variable(container, name= "x")
y = Variable(container, name= "y")
z = Variable(container, name= "z")
c = Variable(container, name= "c")
of = Variable(container, name="ofjective")

# Define equations for variables
x_contrain = Equation(container, "x_contrain", type="regular")
y_contrain = Equation(container, "y_contrain", type="regular")
z_contrain = Equation(container, "z_contrain", type="regular")
of_contrain = Equation(container, "ofjective_contrain", type="regular")

x_contrain[...] =  x >= 0
y_contrain[...] =  (y == x - np.dot(A_param.T, z)) & (y >= 0)
z_contrain[...] =  0 <= z <= D_param
of_contrain[...] = np.dot(c.T, x) - np.dot((l_param - q_param).T, z) - np.dot(s_param.T, y)
# Solve the model with parameters
model = Model(
    container,
    name="SP",
    equations=container.getEquations(),
    problem="SP",
    sense="min",
    objective=of,
)
model.solve()

# Print the results
print("Objective Function Value:  ", round(of.toValue(), 4), "\n")
print("x:  ", round(x.toValue(), 4))
print("y:  ", round(y.toValue(), 4))
print("z:  ", round(z.toValue(), 4))



# Save the GAMS model
#model.export("2SLPWR_Model.gms")