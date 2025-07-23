# num1 and num2 are integers
num1 = 100
num2 = 2

# num3 and num4 are strings
num3 = "50"
num4 = "5"

# Convert string variables to numbers so the math works
num3 = float(num3)
num4 = float(num4)

# This will work fine
print(num1 / num2)

# This will cause an error — do NOT change this line!
print(num3 / num4)