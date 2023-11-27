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

# Tạo mảng 1 chiều


# Tạo mảng 2 chiều
arr1d = [5, 10, 20, 80]
arr0d = 5
arr2d = [[5, 350,80], [10, 600,81], [20, 69, 82], [80, 100, 83]]
capacities = [["seattle", 350], ["san-diego", 600]]
container = Container(delayed_execution=True)
model_name = "MyModel"
problem_type = "MIN"



setArr = Set(container, name = "setArr", records= arr1d)
arr2d_param = Parameter(container, "b", domain=[setArr, setArr], records=arr2d)

A_list = A.tolist()
print("A_list: \n", A_list)
print("arr2d: \n", arr2d)
A_row = [row[0] for row in A_list]
setA = Set(container, name = "setA", records= A_row)

print("list A_row: \n", A_row)
print("list A: \n", A)
print("type A_row: ", type(A_row))
print("type A: ", type(A))
print("type A_list: ", type(A_list))
print("type setArr: ", type(setArr))
print("type setA: ", type(setA))
print("type arr2d: ", type(arr2d))

print("A_row: \n",A_row)
A_param  = Parameter(container, "A", domain = [setA, setA, setA, setA], records= A_list)
