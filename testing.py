a = 0

def change():
    global a
    a = a + 1
    return "test"

text = change()
print(text)
print(a)