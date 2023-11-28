import numpy as np
from gamspy import Model, Container, Set, Parameter, Variable, Equation

"""
* using vector to build for code
error: multi definition for 1 more Set
Exception: Encountered data errors with symbol `D_set`. Possible causes are from duplicate records and/or domain violations.

Use 'hasDuplicateRecords', 'findDuplicateRecords', 'dropDuplicateRecords', 
and/or 'countDuplicateRecords' to find/resolve duplicate records.

Use 'hasDomainViolations', 'findDomainViolations', 'dropDomainViolations', 
and/or 'countDomainViolations' to find/resolve domain violations.

* tasks bạn có thể làm vào ngày mai:
copy D từ main2.py sang, đồng nghĩa với việc xóa z_param và thay đổi z_var thành 1 list x element
"""

# Set up the model
n = 8
m = 5
S = 2
ps = 1/2
MAX_VALUE = 100
l = np.random.uniform(0, MAX_VALUE + 1, n)
q = l + np.random.uniform(1, MAX_VALUE + 1, n)

s = np.random.uniform(0, MAX_VALUE + 1, m)
c = s + np.random.uniform(1, MAX_VALUE + 1, m)

A = np.random.uniform(0, MAX_VALUE + 1, size=(n, m))

D = np.random.binomial(10, 0.5, n)
D[D <= 0] = 0
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

# Define sets
c_tranpose = c.T
c_set = Set(container, name = "c_set", records= c_tranpose)

l_sub_q_tranpose = (l - q).T
l_sub_q_set = Set(container, name = "l_set", records= l_sub_q_tranpose)

s_tranpose = s.T
s_set = Set(container, name = "s_set", records= s_tranpose)
D_set = Set(container, name = "D_set", records= D.tolist())

A_tranpose = A.T
A_list = A_tranpose.tolist()
A_col = []
A_set = []
for j in range(n):
    col_data = [A_list[i][j] for i in range(m)]
    A_col.append(col_data)
for i in range(n):
    A_set.append( Set(container, name = f"A_set{i}", records= A_col[i]) ) 

# Define parameters
c_param = Parameter(container, "c_param", domain=c_set )
l_sub_q_param = Parameter(container, "l_sub_q_param", domain=l_sub_q_set)
s_param = Parameter(container, "s_param", domain=s_set )
D_param = Parameter(container, "D_param", domain=D_set )
A_param  = Parameter(container, "A_param", domain = [A_set[i] for i in range(n-1)], records= A_list)

# Define variables
x_var = Variable(container, name= "x")
y_var = Variable(container, name= "y")
z_var = Variable(container, name= "z")
of = Variable(container, name="objective")

# Define equations for variables
x_contrain = Equation(container, "x_contrain", type="regular")
y_contrain = Equation(container, "y_contrain", type="regular")
z_contrain = Equation(container, "z_contrain", type="regular")
of_contrain = Equation(container, "objective_contrain", type="regular")

x_contrain[...] =  x_var >= 0
y_contrain[...] =  (y_var == x_var - A_param * z_var) and (y_var >= 0)
z_contrain[...] =  (0 <= z_var) and (z_var <= D_param)
of_contrain[...] = of == c_param * x_var + l_sub_q_param * z_var - s_param * y_var

# Solve the model with parameters
model = Model(
    container,
    name="LP",
    equations=container.getEquations(),
    problem="EMP",
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