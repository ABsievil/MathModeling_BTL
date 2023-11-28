import numpy as np
from gamspy import Model, Container, Set, Parameter, Variable, Equation

"""
* using index 
4.11 28/11 : đã chỉnh x,y,z >=1 thì thấy hiện tượng trường value của x y z có biến đổi khá đẹp, nhưng Obj thì không
hint: nên xem lại phạm vi random của các vector, matrix và contrain 
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

D = [np.random.binomial(10, 0.5, n) for _ in range(S)]
D = [np.clip(arr, a_min=0, a_max=None) for arr in D]
D_list = [arr.tolist() for arr in D]

print("c: ",c)
print("l: ",l)
print("q: ",q)
print("s: ",s)
print("D_list: ",D_list)
print("A: \n",A)

#====================
# Create GAMS model with Container
container = Container(delayed_execution=True)

# Define variables
x = [Variable(container, name=f"x_{i}") for i in range(m)]
y = [Variable(container, name=f"y_{i}") for i in range(m)]
z = [Variable(container, name=f"z_{i}") for i in range(n)]
y2 = [Variable(container, name=f"y2_{i}") for i in range(m)]
z2 = [Variable(container, name=f"z2_{i}") for i in range(n)]
of = Variable(container, name="objective")

# Define equations for variables
x_contrain = [Equation(container, f"x_contrain{i}", type="regular") for i in range(m)]
y_contrain = [Equation(container, f"y_contrain{i}", type="regular") for i in range(m)]
z_contrain = [Equation(container, f"z_contrain{i}", type="regular") for i in range(n)]
y2_contrain = [Equation(container, f"y2_contrain{i}", type="regular") for i in range(m)]
z2_contrain = [Equation(container, f"z2_contrain{i}", type="regular") for i in range(n)]
of_contrain = Equation(container, "objective_contrain", type="regular")

# Define contrains for variables
for i in range(m):
    x_contrain[i][...] = x[i] >= 1                                 # x >=0 

for i in range(n):
    z_contrain[i][...] = (1 <= z[i]) and (z[i] <= D_list[0][i])     # 0 <= z <= D
    z2_contrain[i][...] = (z2[i] <= D_list[1][i])                   # 0 <= z2 <= D

for j in range(m):
    sum_expr = sum(A[i][j] * z[i] for i in range(n))
    y_contrain[j][...] =  (y[j] == x[j] - sum_expr) and (y[j] >=1)     # y= x - A.T * z && y >=0
    sum_expr2 = sum(A[i][j] * z2[i] for i in range(n))
    y2_contrain[j][...] =  (y2[j] == x[j] - sum_expr) and (y2[j] >=1)  # y2= x - A.T * z2 && y2 >=0

# Calulate for objection function value
oneStage = sum(c[i] * x[i] for i in range(m))                      # c.T * x

twoStage_first1 = sum( ((l[i] - q[i])*z[i]) for i in range(n) )         #(l - q).T * z
twoStage_second1 = sum(s[j] * y[j] for j in range(m))               # s.T * y

twoStage_first2 = sum( ((l[i] - q[i])*z2[i]) for i in range(n) )         #(l - q).T * z2
two_Stage_second2 = sum(s[j] * y2[j] for j in range(m))               # s.T * y2

of_contrain[...] = of ==  oneStage + ps*(twoStage_first1 - twoStage_second1) + ps*(twoStage_first2 - two_Stage_second2)

# Solve the model with parameters
model = Model(
    container,
    name="myModel",
    equations=container.getEquations(),
    problem="NLP",
    sense="MIN",
    objective=of,
)
model.solve()

# Print the results
print("Objective Function Value:  ", round(of.toValue(), 4), "\n")
print("x:  ", [round(x[i].toValue(), 4) for i in range(m)])
print("y:  ", [round(y[i].toValue(), 4) for i in range(m)])
print("y2:  ", [round(y2[i].toValue(), 4) for i in range(m)])
print("z:  ", [round(z[i].toValue(), 4) for i in range(n)])
print("z2:  ", [round(z2[i].toValue(), 4) for i in range(n)])

# Save the GAMS model
#model.export("my_Model.gms")