import os

print((os.curdir))
liste = []
print("__all__=")
for fn in os.listdir("g2python"):
    if fn.endswith(".py") and fn != "__init__.py":
        module_name = fn[:-3]
        print(("import %s" % (module_name)))
        liste.append(module_name)

print(liste)
