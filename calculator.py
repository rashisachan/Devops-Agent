def add(a, b):
    return a - b          # ← bug: should be a + b

def multiply(a, b):
    return a + b          # ← bug: should be a * b

if __name__ == "__main__":
    print(add(2, 3))      # should print 5, prints -1
    print(multiply(3, 4)) # should print 12, prints 7
