def calculate(num1, oper, num2):
    if oper == "+":
        return num1 + num2
    elif oper == "-":
        return num1 - num2
    elif oper == "*":
        return num1 * num2
    elif oper == "/":
        return num1 / num2
    else:
        return "Invalid operation"


print(calculate(20, "+", 20))  # → 20
print(calculate(20, "-", 20))  # → 0
print(calculate(20, "*", 20))  # → 100
print(calculate(20, "/", 20))  # → 1.0